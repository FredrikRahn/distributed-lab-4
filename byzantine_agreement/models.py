'''
Models module
'''

def vote_data(node_id, vote):
    '''
    Vote model
    '''

    model = {
        'node_id': node_id,
        'vote': vote
    }

    return model

def byzantine_vote_input(no_round, no_nodes, no_loyal, on_tie):
    '''
    Byzantine vote model
    '''
    model = {
        'no_round': no_round,
        'no_nodes': no_nodes,
        'no_loyal': no_loyal,
        'on_tie': on_tie
    }

    return model
