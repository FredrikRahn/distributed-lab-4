'''
Honest general class
'''
from random import randint

from general import General


class Honest(General):
    """
    Honest class
        :param General: Parent class
    """

    def __init__(self):
        # Run init on extended General class
        super(Honest, self).__init__()
        self.myProfile = 'Honest'

    def vote_attack(self):
        """
        TODO: Implement
            :param self: temp
        """
        print 'Voted Attack'
        return True

    def vote_retreat(self):
        """
        TODO: Implement
            :param self: temp
        """
        print 'Voted Retreat'
        return False

    def vote(self):
        """
        TODO: Implement
            :param self: temp
        """

        # TODO: Add logic on how to decide votes
        # For now just do dice roll with 50/50 chance

        roll = randint(1, 100)
        if roll <= 50:
            return 'Attack'
        else:
            return 'Retreat'
