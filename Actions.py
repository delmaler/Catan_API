from Board import Road
from Board import Crossroad
from Board import Terrain
from Hand import Hand
from Log import Log
from Log import StatisticsLogger
from Resources import SETTLEMENT_PRICE
from Resources import ROAD_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
from API import API
from Auxilary import r2s
from Resources import Resource
from abc import ABC
import math
from random import randrange
from random import uniform

api: API


class Action(ABC):
    def __init__(self, hand: Hand, heuristic_method):
        self.hand = hand
        self.points = self.hand.points  # how many points the player has before the action get executed
        self.heuristic_method = heuristic_method
        # self.heuristic = hand.heuristic if self.heuristic_method is None else self.heuristic_method(self)
        self.name = 'action'
        self.heuristic = uniform(0, 1) if heuristic_method is None else heuristic_method(self)
        self.log = self.hand.board.log  # type: Log
        self.statistics_logger = self.hand.board.statistics_logger  # type: StatisticsLogger

    def do_action(self):
        self.hand.heuristic = self.heuristic

    def log_action(self):
        # ToDo: build statistic based on the name of the player (on Dork, Guru, or NNPlayer)
        history_log = {'name': self.name, 'player': self.hand.index}
        self.log.action(history_log)

    def tmp_do(self):
        pass

    def undo(self):
        pass

    def shared_aftermath(self):
        api.print_action(self.name)
        api.print_resources(self.hand.index, self.hand.resources)
        api.save_file()
        api.delete_action()
        self.log_action()
        statistic_keys = self.create_keys()
        self.statistics_logger.save_action(statistic_keys, self.hand.index)

    def create_keys(self):
        return [self.name, self.points, self.hand.name]


class DoNothing(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'do nothing'

    # ToDo: check correctness
    def do_action(self):
        pass

    # Todo: move to heuristic
    def compute_heuristic(self):
        return self.hand.heuristic

    def create_keys(self):
        keys = super().create_keys()
        # ToDo: DoNothing should get next best action heuristic score in __init__ as key
        return keys


class UseDevCard(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'use development card'

    def do_action(self):
        super().do_action()
        self.shared_aftermath()


class UseKnight(UseDevCard):
    def __init__(self, hand, heuristic_method, terrain, dst):
        super().__init__(hand, heuristic_method)
        self.terrain = terrain
        self.dst = dst
        self.name = 'use knight'

    # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.use_knight()
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    # Todo: move to heuristic
    def compute_heuristic(self):
        resource = self.use_knight()
        new_heuristic = self.hand.heuristic
        self.undo_use_knight(resource, self.terrain)
        return new_heuristic

    # terrain = where to put the bandit
    # dst = from who to steal
    def use_knight(self):
        hand = self.hand
        terrain = self.terrain
        for knight in hand.cards["knight"]:
            if knight.is_valid():
                if terrain.put_bandit():
                    hand.cards["knight"].remove(knight)
                    return self.steal()
        return None

    # todo test it
    def undo_use_knight(self, resource: Resource, terrain: Terrain):
        dst = self.hand.board.hands[self.dst]
        assert terrain is not None
        terrain.put_bandit()
        if resource is not None:
            self.hand.resources[resource] -= 1
            dst.resources[resource] += 1

    def steal(self):
        dst = self.hand.board.hands[self.dst]
        resources = dst.get_resources_number()
        if resources == 0:
            return None
        index = randrange(resources)
        for resource in dst.resources.keys():
            if dst.resources[resource] >= index:
                self.hand.resources[resource] += 1
                dst.resources[resource] -= 1
                return resource
            else:
                index -= dst.resources[resource]

    def create_keys(self):
        keys = super(UseKnight, self).create_keys()
        n_i, p_i = self.hand.board.bandit_location.bandit_value(self.hand.index)
        n_f, p_f = self.terrain.bandit_value(self.hand.index)
        keys += [n_i - n_f, p_f - p_i]
        return keys


class UseMonopole(UseDevCard):
    def __init__(self, player, heuristic_method, resource):
        assert resource != Resource.DESSERT
        super().__init__(player, heuristic_method)
        self.resource = resource
        self.name = 'use monopole'
        # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.use_monopole()
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    # Todo: move to heuristic
    def compute_heuristic(self):
        selected_resource_quantity = 0
        for hand in self.hand.board.hands:
            selected_resource_quantity += hand.resources[self.resource]
        return self.hand.parameters.resource_value[self.resource] * selected_resource_quantity

    def use_monopole(self):
        for index, card in enumerate(self.hand.cards["monopole"]):
            if card.is_valid():
                self.hand.cards["monopole"].pop(index)
                for hand in self.hand.board.hands:
                    if hand.index != self.hand.index:
                        self.hand.resources[self.resource] += hand.resources[self.resource]
                        hand.resources[self.resource] = 0

    def create_keys(self):
        keys = super().create_keys()
        take = 0
        for hand in self.hand.board.hands:
            if hand != self.hand:
                take += hand.resources[self.resource]
        keys += [take]
        return keys


class UseYearOfPlenty(UseDevCard):
    def __init__(self, hand, heuristic_method, resource1, resource2):
        super().__init__(hand, heuristic_method)
        self.resource1 = resource1
        self.resource2 = resource2
        # self.heuristic += self.compute_heuristic()
        self.name = 'use year of plenty'

    def do_action(self):
        super().do_action()
        self.use_year_of_plenty()
        # self.heuristic += self.compute_heuristic()
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    def compute_heuristic(self):
        return self.hand.parameters.resource_value[self.resource1] + self.hand.parameters.resource_value[self.resource2]

    def use_year_of_plenty(self):
        for card in self.hand.cards["year of prosper"]:
            if card.is_valid():
                self.hand.resources[self.resource1] += 1
                self.hand.resources[self.resource2] += 1
                self.hand.cards["year of prosper"].remove(card)


class UseBuildRoads(UseDevCard):
    def __init__(self, hand, heuristic_method, road1: Road, road2: Road):
        super().__init__(hand, heuristic_method)
        self.road1 = road1
        self.road2 = road2
        self.name = 'use build roads'
        # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.build_2_roads()
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    # ToDo: fix
    def compute_heuristic(self):
        heuristic_increment = 0
        old_road_length = self.hand.parameters.longest_road_value
        build_road1 = BuildRoad(self.hand, self.heuristic_method, self.road1)
        build_road2 = BuildRoad(self.hand, self.heuristic_method, self.road2)
        build_road1.tmp_do()
        build_road2.tmp_do()
        if self.hand.board.longest_road_owner != self.hand.index:
            heuristic_increment += (self.hand.board.longest_road_owner == self.hand.index) * 5
        heuristic_increment += self.hand.parameters.longest_road_value - old_road_length
        # hand_heuristic = self.hand.heuristic
        build_road1.undo()
        build_road2.undo()
        return heuristic_increment

    def build_2_roads(self):
        hand = self.hand  # type: Hand
        road1 = self.road1  # type: Road
        road2 = self.road2  # type: Road
        player = hand.index
        for index, card in enumerate(hand.cards["road builder"]):
            if card.is_valid():
                self.hand.cards["road builder"].pop(index)
                if road1.is_legal(player) and road2.is_legal(player):
                    # self.heuristic += self.compute_heuristic()
                    road1.build(hand.index)
                    road2.build(hand.index)
                    hand.cards["road building"].remove(card)
                    return True
        return False


class UseVictoryPoint(UseDevCard):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = "use victory_point"
        # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.use_victory_point()
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    def compute_heuristic(self):
        if len(list(filter(lambda x: x.ok_to_use, self.hand.cards["victory points"]))) + self.hand.points >= 10:
            return math.inf
        else:
            return -100

    def use_victory_point(self):
        hand = self.hand
        hand.points += len(hand.cards['victory points'])
        hand.heuristic -= 1000
        if hand.points >= 10:
            hand.heuristic += math.inf


class BuildSettlement(Action):
    def __init__(self, hand, heuristic_method, crossroad: Crossroad):
        self.crossroad = crossroad
        super().__init__(hand, heuristic_method)
        self.name = 'build settlement'
        # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.buy_settlement()
        self.action_aftermath()

    def action_aftermath(self):
        i, j = self.crossroad.location
        api.print_action(self.name)
        api.print_settlement(self.hand.index, i, j)
        api.point_on_crossroad(i, j)
        # ToDo : give a more meaningful type
        self.shared_aftermath()

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay(SETTLEMENT_PRICE)

    def buy_settlement(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        hand.pay(SETTLEMENT_PRICE)
        self.create_settlement()
        # prioritize having a variety of resource produce
        self.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            self.heuristic += (hand.production[resource] - old_production[resource]) * hand.parameters.resource_value[
                resource]

        hand.update_resource_values()
        hand.settlements_log += [self.crossroad]

    def compute_heuristic(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        legals = self.crossroad.tmp_build(self.hand.index)
        heuristic_increment = len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            heuristic_increment += (hand.production[resource] - old_production[resource]) * \
                                   hand.parameters.resource_value[resource]
        self.crossroad.unbuild(self.hand.index, legals)
        return heuristic_increment

    def create_settlement(self):
        hand = self.hand
        self.crossroad.connected[hand.index] = True
        hand.settlement_pieces -= 1
        hand.points += 1
        for resource in Resource:
            if resource is not Resource.DESSERT:
                hand.production_all += self.crossroad.val[resource] / 36
        self.crossroad.build(hand.index)
        hand.set_distances()
        if self.crossroad.port is not None:
            hand.ports.add(self.crossroad.port)

    def create_keys(self):
        keys = super().create_keys()
        keys += [self.crossroad.val['sum']]
        for resource in Resource:
            if resource != Resource.DESSERT:
                keys += [self.crossroad.val[resource]]
        return keys


class BuildFirstSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build first settlement'

    def do_action(self):
        self.create_settlement()
        self.action_aftermath()

    def is_legal(self):
        return True


class BuildSecondSettlement(BuildSettlement):
    def __init__(self, hand, heuristic_method, crossroad):
        super().__init__(hand, heuristic_method, crossroad)
        self.name = 'build second settlement'

    def do_action(self):
        self.create_settlement()
        self.crossroad.produce(self.hand.index)
        self.action_aftermath()

    def is_legal(self):
        return True


class BuildCity(Action):
    def __init__(self, hand, heuristic_method, crossroad: Crossroad):
        super().__init__(hand, heuristic_method)
        self.crossroad = crossroad
        # self.heuristic += self.compute_heuristic()
        self.name = 'build city'

    def do_action(self):
        self.buy_city()
        self.action_aftermath()

    def action_aftermath(self):
        i, j = self.crossroad.location
        api.print_action(self.name)
        api.print_city(self.hand.index, i, j)
        api.point_on_crossroad(i, j)
        self.shared_aftermath()

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.crossroad.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay(CITY_PRICE)

    def buy_city(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        hand.pay(CITY_PRICE)
        self.create_city()
        self.heuristic += len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            self.heuristic += (hand.production[resource] - old_production[resource]) * hand.parameters.resource_value[
                resource]

        hand.update_resource_values()
        hand.cities += [self.crossroad]

    def create_city(self):
        hand = self.hand
        hand.settlement_pieces += 1
        hand.city_pieces -= 1
        hand.points += 1
        self.crossroad.build(hand.index)
        hand.set_distances()

    def compute_heuristic(self):
        hand = self.hand
        old_production_variety = len(list(filter(lambda x: x.value != 0, hand.production)))
        old_production = hand.production
        legals = self.crossroad.tmp_build(self.hand.index)
        heuristic_increment = len(list(filter(lambda x: x.value != 0, hand.production))) - old_production_variety
        for resource in hand.production:
            heuristic_increment += (hand.production[resource] - old_production[resource]) * \
                                   hand.parameters.resource_value[resource]
        self.crossroad.unbuild(self.hand.index, legals)
        return heuristic_increment

    def create_keys(self):
        keys = super().create_keys()
        keys += [self.crossroad.val['sum']]
        for resource in Resource:
            if resource != Resource.DESSERT:
                keys += [self.crossroad.val[resource]]
        return keys


class BuildRoad(Action):
    def __init__(self, hand, heuristic_method, road: Road):
        super().__init__(hand, heuristic_method)
        self.road = road
        self.name = 'build road'

    def do_action(self):
        super().do_action()
        self.buy_road()
        self.action_aftermath()

    def action_aftermath(self):
        api.print_action(self.name)
        api.write_a_note(str(self.check_longest_road()))
        i0, j0 = self.road.neighbors[0].location
        i1, j1 = self.road.neighbors[1].location
        api.print_road(self.hand.index, i0, j0, i1, j1)
        api.point_on_road(i0, j0, i1, j1)
        self.shared_aftermath()

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'location': self.road.location_log()
        }
        self.log.action(log)

    def is_legal(self):
        if self.hand.can_pay(ROAD_PRICE):
            return True
        else:
            return False

    def buy_road(self):
        hand = self.hand
        hand.pay(ROAD_PRICE)
        self.create_road()
        return

    # ---- take a temporary action ---- #

    def tmp_do(self):
        if self.hand.can_buy_road() and self.road.is_legal(self.hand.index):
            self.hand.pay(ROAD_PRICE)
            self.road.temp_build(self.hand.index)

    # ---- undo an action ---- #

    def undo(self):
        self.hand.receive(ROAD_PRICE)
        self.road.undo_build()

    def create_road(self):
        self.hand.road_pieces -= 1
        self.road.build(self.hand.index)
        self.hand.set_distances()

    def compute_heuristic(self):
        heuristic_increment = 0
        old_road_length = self.hand.parameters.longest_road_value
        build_road = BuildRoad(self.hand, self.heuristic_method, self.road)
        build_road.tmp_do()
        if self.hand.board.longest_road_owner != self.hand.index:
            heuristic_increment += (self.hand.board.longest_road_owner == self.hand.index) \
                                   * self.hand.parameters.longest_road_value
        heuristic_increment += self.hand.parameters.longest_road_value - old_road_length
        build_road.undo()
        return heuristic_increment

    def travel_left(self, cr: Crossroad, roads, right):
        end = True
        longest_road = roads
        for n in cr.neighbors:
            if n.road.owner == self.hand.index and n.road.traveled is not True:
                end = False
                n.road.traveled = True
                current_road = self.travel_left(n.crossroad, roads + 1, right)
                n.road.traveled = False
                if longest_road < current_road:
                    longest_road = current_road
        if end:
            return roads + self.travel_right(right, 0) + 1
        else:
            return longest_road

    def travel_right(self, cr: Crossroad, roads):
        longest_right_road = roads
        for n in cr.neighbors:
            if n.road.owner == self.hand.index and n.road.traveled is not True:
                n.road.traveled = True
                right_road = self.travel_right(n.crossroad, roads + 1)
                n.road.traveled = False
                if longest_right_road < right_road:
                    longest_right_road = right_road
        return longest_right_road

    def check_longest_road(self):
        left, right = self.road.neighbors  # type: Crossroad
        self.road.traveled = True
        longest_road = self.travel_left(left, 0, right)
        self.road.traveled = False
        return longest_road


class BuildFreeRoad(BuildRoad):
    def __init__(self, player, heuristic_method, road):
        super().__init__(player, heuristic_method, road)
        self.name = 'build free road'

    def do_action(self):
        self.create_road()
        self.action_aftermath()

    def is_legal(self):
        return True


class Trade(Action):
    def __init__(self, hand, heuristic_method, src, exchange_rate, dst, take):
        super().__init__(hand, heuristic_method)
        self.src = src
        self.dst = dst
        self.take = take
        self.give = take * exchange_rate
        self.name = 'trade'
        self.exchange_rate = exchange_rate

    def do_action(self):
        super().do_action()
        self.trade()
        api.trade(self.hand.board.players, self.hand.index, self.src, self.dst, self.give, self.take)
        self.shared_aftermath()

    # todo
    def compute_heuristic(self):
        pass

    def log_action(self):
        log = {
            'name': self.name,
            'player': self.hand.index,
            'source': r2s(self.src),
            'destination': r2s(self.dst),
            'take': self.take,
            'give': self.give
        }
        self.log.action(log)

    def is_legal(self):
        return self.hand.can_pay({self.src: self.give})

    def trade(self):
        self.hand.resources[self.src] -= self.give
        self.hand.resources[self.dst] += self.take

    def create_keys(self):
        keys = super().create_keys()
        keys += [self.exchange_rate]
        return keys


class BuyDevCard(Action):
    def __init__(self, hand, heuristic_method):
        super().__init__(hand, heuristic_method)
        self.name = 'buy devCard'
        # self.heuristic += self.compute_heuristic()

    def do_action(self):
        super().do_action()
        self.buy_development_card()

    def compute_heuristic(self):
        return self.hand.parameters.dev_card_value

    def buy_development_card(self):
        hand = self.hand
        stack = self.hand.board.devStack
        hand.pay(DEV_PRICE)
        card = stack.get()
        hand.cards[card.name] += [card]


class ThrowCards(Action):
    def __init__(self, hand: Hand, heuristic, cards):
        self.cards = cards
        super().__init__(hand, heuristic)
        self.name = "throw cards"

    def do_action(self):
        for resource in self.cards:
            self.hand.resources[resource] -= self.cards[resource]
