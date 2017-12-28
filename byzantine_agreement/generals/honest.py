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
        # Init my_profile var to easily check class of node
        self.my_profile = 'Honest'
        # Init my_vote for readability
        self.my_vote = None

    def vote_attack(self):
        """
        TODO: Implement
            :param self: temp
        """
        print 'Voted Attack'
        self.my_vote = True
        return self.my_vote

    def vote_retreat(self):
        """
        TODO: Implement
            :param self: temp
        """
        print 'Voted Retreat'
        self.my_vote = False
        return self.my_vote
