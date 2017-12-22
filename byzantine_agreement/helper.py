'''
 This module handles extraction of endpoints from requests
'''

def extract_ep(path):
    """
    Extracts the endpoint(s) from request path
        :param path: raw request path
    """
    return path[1::].split('/')
