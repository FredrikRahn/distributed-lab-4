'''
Honest general class
'''
from random import randint

from general import General

class Honest(General):

    def __init__(self):
        General.__init__(self)
        self.profile = 'Honest'
        self.vote = self.decide_vote()

        if self.vote == 'Attack':
            self.vote_attack()
        elif self.vote == 'Retreat':
            self.vote_retreat()
        else:
            raise TypeError('Vote failed. Unknown type')

    def vote_attack(self):
        print 'Voted Attack'
        return True

    def vote_retreat(self):
        print 'Voted Retreat'
        return False

    def decide_vote(self):
        #TODO: Add logic on how to decide votes
        # For now just do dice roll with 50/50 chance

        roll = randint(1,100)
        if roll < 50:
            return 'Attack'
        else:
            return 'Retreat'
    