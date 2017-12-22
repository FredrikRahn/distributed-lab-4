'''
Byzantine class
'''
from general import General

class Byzantine(General):

    def __init__(self):
        General.__init__(self)
        self.profile = 'Byzantine'

    def vote_round1(self, no_loyal, on_tie):
        """
        Handle voting for round 1
            :param no_loyal: number of loyal nodes
            :param on_tie: Decision on tie, True/False (Attack/Retreat)
        """
        result_vote = []
        for i in range(0, no_loyal):
            if i % 2 == 0:
                result_vote.append(not on_tie)
            else:
                result_vote.append(on_tie)
        return result_vote

    def vote_round2(self, no_loyal, no_total, on_tie):
        """
        Compute byzantine votes for round 2, trying to swing the decision
            :param no_loyal: number of loyal nodes
            :param no_total: number of total nodes
            :param on_tie: decision on tie, True/False (Attack/Retreat)
        """

        result_vectors = []
        for i in range(0, no_loyal):
            if i % 2 == 0:
                result_vectors.append([on_tie] * no_total)
            else:
                result_vectors.append([not on_tie] * no_total)
        return result_vectors
