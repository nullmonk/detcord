'''
Random exceptions for the program
'''

class DetfileNotFound(Exception):
    '''
    We need a detfile to run the program
    '''
    pass


class HostNotFound(Exception):
    '''
    Thrown whenever a host is not found
    '''
    pass
