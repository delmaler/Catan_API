import random


class Die:
    def __init__(self):
        self.number = random.randrange(1, 6)

    def __str__(self):
        return str(self.number)

    def throw(self):
        self.number = random.randrange(1, 6)


class Dice:
    def __init__(self):
        self.dice1 = Die()
        self.dice2 = Die()
        self.sum = self.dice1.number + self.dice2.number

    def __str__(self):
        return str(self.sum)

    def throw(self):
        self.dice1.throw()
        self.dice2.throw()
        self.sum = self.dice1.number + self.dice2.number


def test_dice():
    print("Testing dice:")
    dice = Die()
    print("   Initial state: " + str(dice))
    dice.throw()
    print("   After throw: " + str(dice))

def test_Dices():
    print("Testing Dices:")
    dices = Dice()
    print("   Initial state: first dice is "+str(dices.dice1)+", second dice is "+str(dices.dice2)+" and the sum is "+str(dices))
    dices.throw()
    print("   Initial state: first dice is "+str(dices.dice1)+", second dice is "+str(dices.dice2)+" and the sum is "+str(dices))

test_dice()
test_Dices()