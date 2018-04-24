import datetime
from urllib.request import urlretrieve as wget

def saveResults(path, result):
    '''Write the output of a command to the given path
    '''
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, 'a') as of:
            of.write(now+"\n")
            of.write(result.stdout)
            of.write("\n-- Stderr --\n")
            of.write(result.stderr)
        return True
    except Exception as E:
        print(E)
        return False

def logAction(action, host=""):
    '''Write a log to a logfile
    '''
    try:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        with open("logs/actions.log", 'a') as of:
            of.write("{}: [{}] {}\n".format(now, host, action))
        return True
    except Exception as E:
        return False
