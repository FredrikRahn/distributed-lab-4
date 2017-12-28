'''
Define General class that extends a role
'''

from random import randint
from multiprocessing import Process, Lock

class General(object):
    """
    General class, assigned to all nodes until they've chosen another
    """
    # Vars shared by all Generals
    lock = Lock()
    # # For now set #Byzantine allowed to 1
    # nrByzantineAllowed = 1
    # # Keep track of how many generals that has chosen Byzantine
    # byzantine_chosen = 0
    # # Numbers rolled, to force last node into Byzantine if noone has chosen it
    # times_rolled = 0

    def __init__(self):
        # Init profile to None
        self.my_profile = 'General'

        # Init empty vote vector
        self.vote_vector = {}

        # Init empty Result vector
        self.result_vector = {}

    def add_to_vote_vector(self, node_id, vote):
        self.vote_vector[node_id] = vote

    # def choose_role(self, numberOfNodes):
    #     """
    #     Chooses a role for a general
    #         :param numberOfNodes: Number of nodes in the network
    #     """
    #     # Try and acquire shared general lock
    #     General.lock.acquire()

    #     #If noone has chosen byzantine, force the last node to choose byzantine
    #     if General.byzantine_chosen < 1 and General.times_rolled == numberOfNodes - 1:
    #         General.times_rolled += 1
    #         General.byzantine_chosen += 1

    #         # Set profile, release lock and return
    #         General.lock.release()
    #         self.profile = 'Byzantine'
    #         print 'Profile set as Byzantine'
    #         return self.profile

    #     elif General.byzantine_chosen < General.nrByzantineAllowed:
    #         roll = self.roll_dice(numberOfNodes)
    #         General.times_rolled += 1

    #         if roll < numberOfNodes / 2:
    #             General.byzantine_chosen += 1
    #             # Set profile, release lock and return
    #             General.lock.release()
    #             self.profile = 'Byzantine'
    #             print 'Profile set as Byzantine'
    #             return self.profile
    #         else:
    #             # Set profile, release lock and return
    #             General.lock.release()
    #             self.profile = 'Honest'
    #             print 'Profile set as Honest'
    #             return self.profile
    #     else:
    #         # Max amount of Byzantine reached
    #         # Set profile to honest, release lock and return
    #         General.lock.release()
    #         self.profile = 'Honest'
    #         print 'Profile set as Honest'
    #         return self.profile

    # def roll_dice(self, numberOfNodes):
    #     """
    #     Roll the dice
    #         :param numberOfNodes: #nodes is used as max roll
    #     """
    #     roll = randint(1, numberOfNodes)
    #     return roll
