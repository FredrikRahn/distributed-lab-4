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

    def build_vote_result(self, results):
        '''
        Updates the voting result template
        '''
        return self.vote_result % results
