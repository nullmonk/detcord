'''
Random exceptions for the program
'''

class InvalidDetfile(Exception):
    '''
    We need a detfile
    '''
    pass

class NoConnection(Exception):
    '''
    We need a detfile
    '''
    pass


class HostNotFound(Exception):
    '''
    Thrown whenever a host is not found
    '''
    pass
