from Board import Board
import Dice
from Player import Player
import DevStack


class Game:
    def buy_dev_card(self, player):
        if player.buy_devops():
            player.devCards.append(self.devStack.get())

    def __init__(self, players):
        self.round = 0
        self.turn = 0
        self.board = Board(players)
        self.players = []
        for i in range(players):
            player = Player(i, self.board)
            self.players += [player]

    def start_game(self):
        for i in range(len(self.players)):
            if self.players[i].is_computer:
                self.players[i].computer_1st_settlement(self.players[i].index)
            else:
                pass
            self.next_turn()
        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_computer:
                self.players[i].computer_2nd_settlement(self.players[i].index)
            else:
                pass
            self.next_turn()

    def throw_dice(self):
        for i, j in self.board.dice.throw():
            self.board.map[i][j].produce()

    def next_turn(self):
        self.turn += 1
        if self.turn == len(self.players):
            self.turn = 0
            self.round += 1
        self.board.next_turn(self.turn, self.round)

    def play_round(self):
        for player in self.players:
            self.play_turn(player)
            if max(list(map(lambda x: x.points, self.board.hands))) >= 10:
                break
            self.next_turn()

    def play_turn(self, player):
        self.throw_dice()
        if self.players[player.index].is_computer:
            while player.compute_turn():
                pass

    def play_game(self):
        num_players = input("how many players are playing?")
        game = Game(int(num_players))
        game.start_game()
        while max(list(map(lambda x: x.points, game.board.hands))) < 10:
            game.play_round()
            print(game.round)
            for hand in self.board.hands:
                for typeCard in hand.cards.values():
                    if typeCard:
                        for card in typeCard:
                            card.ok_to_use = True


# ---- main ---- #


def main():
    game = Game(3)
    game.play_game()

    # print_distance(game)


print("Hello Game")
main()
