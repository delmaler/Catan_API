from Resources import Resource
from Resources import ROAD_PRICE
from Resources import SETTLEMENT_PRICE
from Resources import CITY_PRICE
from Resources import DEV_PRICE
from Auxilary import r2s
import math


class Hand:
    def __init__(self, index, board):
        self.index = index
        self.name = None
        self.points = 0
        # ---- hand ---- #
        self.resources = {Resource.WOOD: 0, Resource.IRON: 0, Resource.WHEAT: 0, Resource.SHEEP: 0, Resource.CLAY: 0}
        self.cards = {"knight": [], "victory points": [], "monopole": [], "road builder": [], "year of prosper": []}
        self.road_pieces = 15
        self.settlement_pieces = 5
        self.city_pieces = 4
        # ---- board --- #
        self.board = board
        self.ports = set()
        self.lands_log = []
        self.settlements_log = []
        self.cities = []
        # ---- achievements and stats ---- #
        self.longest_road, self.largest_army = 0, 0
        self.heuristic = 0
        self.production = {Resource.CLAY: 0, Resource.WOOD: 0, Resource.WHEAT: 0, Resource.IRON: 0,
                           Resource.SHEEP: 0}
        self.production_all = 0
        # ---- these are values that we can manipulate according to success ---- #
        self.longest_road_value = 5
        self.biggest_army_value = 4.5
        self.road_value = 0.2
        self.resource_value = {Resource.CLAY: 1, Resource.WOOD: 1, Resource.WHEAT: 1, Resource.IRON: 1,
                               Resource.SHEEP: 1}
        self.dev_card_value = 0.5

    # ---- get information ---- #

    def compute_2_roads_heuristic(self, road1, road2):
        heuristic_increment = 0
        old_road_length = self.longest_road_value
        if self.board.longest_road_owner != self.index:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
            heuristic_increment += (self.board.longest_road_owner == self.index) * 5
        else:
            self.tmp_buy_road(road1)
            self.tmp_buy_road(road2)
        heuristic_increment += (self.longest_road_value - old_road_length) * self.road_value
        self.undo_buy_road(road2)
        self.undo_buy_road(road1)
        return heuristic_increment

    def get_resources_number(self):
        resource_sum = 0
        for r in self.resources.values():
            resource_sum += r
        return resource_sum

    def get_cards_number(self):
        resource_sum = 0
        for c in self.cards:
            resource_sum += len(c)
        return resource_sum

    def get_lands(self):
        lands = []
        for line in self.board.crossroads:
            for cr in line:
                if cr.connected[self.index] and cr.building == 0 and cr.legal:
                    lands += [cr]
        return lands

    # check if an action can be taken ---- #

    def can_buy_road(self):
        return self.can_pay(ROAD_PRICE) and self.road_pieces

    def can_buy_settlement(self):
        return self.can_pay(SETTLEMENT_PRICE) and self.settlement_pieces

    def can_buy_city(self):
        return self.can_pay(CITY_PRICE) and self.city_pieces

    def can_buy_development_card(self):
        return self.can_pay(DEV_PRICE) and self.board.devStack

    def can_trade(self, src: Resource, amount):
        if src in self.ports:
            return self.resources[src] >= amount * 2, 2
        if Resource.DESSERT in self.ports:
            return self.resources[src] >= amount * 3, 3
        return self.resources[src] >= amount * 4, 4

    # ---- take a temporary action ---- #

    def tmp_buy_road(self, road):
        if self.can_buy_road() and road.is_legal():
            self.resources[Resource.WOOD] -= 1
            self.resources[Resource.CLAY] -= 1
            road.temp_build(self.index)
            return True
        return False

    # ---- undo an action ---- #

    def undo_buy_road(self, road):
        self.resources[Resource.WOOD] += 1
        self.resources[Resource.CLAY] += 1
        road.undo_build(self.index)

    # ---- auxiliary functions ---- #

    def set_distances(self):
        stack = []
        stack_fert = []
        for line in self.board.crossroads:
            for cr in line:
                cr.fertility_dist = math.inf
                if cr.ownership is not None:
                    cr.distance[cr.ownership] = 0
                    stack.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)
                else:
                    if cr.legal:
                        cr.fertility_dist = 0
        while stack:
            cr = stack.pop()
            for n in cr.neighbors:
                ncr = n.crossroad
                for i in range(self.board.players):
                    if cr.distance[i] > ncr.distance[i] + 1:
                        cr.distance[i] = ncr.distance[i] + 1
                        stack.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)
        while stack_fert:
            cr = stack_fert.pop()
            for n in cr.neighbors:
                ncr = n.crossroad
                if cr.fertility_dist > ncr.fertility_dist + 1:
                    cr.fertility_dist = ncr.fertility_dist + 1
                    stack_fert.extend(x.crossroad for x in cr.neighbors if x.crossroad not in stack)

    def can_pay(self, price):
        for resource in price:
            if self.resources[resource] < price[resource]:
                return False
        return True

    def pay(self, price):
        for resource in price:
            self.resources[resource] -= price[resource]

    # ---- test functions ---- #

    def print_resources(self):
        print("resources of player : " + self.name)
        for resource in self.resources:
            print(r2s(resource) + " : " + str(self.resources[resource]) + "|||", end="")
        print()

    def update_resource_values(self):
        pass
