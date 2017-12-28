'''
This module assembles the HTML
'''

import os

# Global vars
# Save path to resources directory
PATH_RESOURCES = os.path.dirname(os.path.realpath(__file__)) + '/resources/'


class HtmlBuilder(object):
    '''
    This class handles the building of HTML
    '''

    def __init__(self):
        '''
        Init the HTML builder
        '''
        self.index = open(PATH_RESOURCES + 'index.html', 'r').read()
        self.profile = open(PATH_RESOURCES + 'profile.html', 'r').read()
        self.vote_result = open(
            PATH_RESOURCES + 'vote_result.html', 'r').read()

    def build_page(self, profile):
        ''' 
        Assemble page HTML
        '''
        page = self.profile % profile + self.index
        return page

    def build_votes_result(self, vote_vector):
        '''
        Updates the voting result template
        '''
        entry = ''
        for key in vote_vector.keys():
            entry += self.vote_result % (str(key) + ' ' + str(vote_vector[key]))
        return entry

    def build_result(self, result_vector, result):
        result = 'Result vector: '
        for vote in result_vector:
            result += self.vote_result % (str(vote) + '\n')
        result += '\n' + 'Result: ' + str(result)
