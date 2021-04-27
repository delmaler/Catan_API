import json
from random import uniform


class Log:
    def __init__(self, players):
        self.round = 0
        self.turn = 0
        self.players = players

        self.turn_log = {'turn': 0, 'actions': []}
        self.round_log = {'round': 0, 'turns': []}
        self.game_log = {'number of players': players, 'rounds': []}
        self.game_log_name = self.create_file_name()

        self.statistic = {}

    def next_turn(self):
        self.round_log['turns'] += [self.turn_log]
        if self.turn == self.players - 1:
            self.turn = 0
            self.round += 1
            self.game_log['rounds'] += [self.round_log]
            self.round_log = {'round': self.round, 'turns': []}
        else:
            self.turn += 1
        self.turn_log = {'turn': self.turn, 'actions': []}

    def dice(self, dice):
        self.turn_log['dice'] = dice

    def action(self, action_log):
        self.turn_log['actions'] += [action_log]

    def end_game(self):
        with open(self.game_log_name, 'w') as outfile:
            json.dump(self.game_log, outfile)
        with open('tracking_development.json') as json_file:
            tracker = json.load(json_file)
            tracker['games'] += [self.round]
        with open('tracking_development.json', 'w') as outfile:
            json.dump(tracker, outfile)

    def board(self, board_log):
        self.game_log['board'] = board_log

    @staticmethod
    def create_file_name():
        with open("saved_games/manager.json") as json_file:
            manager = json.load(json_file)
        name = "saved_games/game" + str(manager['games saved'] + 1) + ".json"
        manager['games saved'] += 1
        with open("saved_games/manager.json", 'w') as outfile:
            json.dump(manager, outfile)
        return name


class StatisticsLogger:
    def __init__(self):
        self.actions = []
        with open("statistics.json") as json_file:
            self.statistics = json.load(json_file)

    def save_action(self, keys, index):
        self.actions += [(index, keys)]

    def analyze_actions(self, winner):
        for action in self.actions:
            win = 1 if winner == action[0] else 0
            pointer = self.statistics['actions']
            for key in action[1]:
                if key in pointer:
                    pointer[key]['events'] += 1
                    pointer[key]['wins'] += win
                else:
                    pointer[key] = {'events': 1, 'wins': win}
                pointer = pointer[key]
        with open('statistics.json', 'w') as out_file:
            json.dump(self.statistics, out_file)

    def get_statistic(self, keys):
        pointer = self.statistics['actions']
        no_info = True
        for key in keys:
            if key in pointer:
                pointer = pointer[key]
                no_info = False
            else:
                if no_info:
                    return uniform(0, 1)
                else:
                    break
        events = pointer['events']
        wins = pointer['wins']
        return wins / events
