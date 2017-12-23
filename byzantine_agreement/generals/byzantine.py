'''
Byzantine class
'''
from general import General


class Byzantine(General):
    """
    Byzantine class
        :param General: Parent class
    """

    def __init__(self):
        # Run init on extended General class
        super(Byzantine, self).__init__()
        self.myProfile = 'Byzantine'

    def vote(self, voting_data):
        """
        Call the respective function depending on the round
            :param no_round: round number
            :param no_loyal: number of loyal nodes
            :param no_total: total number of nodes
            :param on_tie: action on tie
        """

        if voting_data.no_round == 1:
            self.vote_round1(voting_data.no_loyal, voting_data.on_tie)
        elif voting_data.no_round == 2:
            self.vote_round2(voting_data.no_loyal, voting_data.no_total, voting_data.on_tie)
        else:
            raise ValueError, 'Invalid round count'

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
