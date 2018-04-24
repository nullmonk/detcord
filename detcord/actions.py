Action = None
def run(*args, **kwargs):
    return Action.run(*args, **kwargs)

def local(*args, **kwargs):
    return Action.local(*args, **kwargs)

def script(*args, **kwargs):
    return Action.script(*args, **kwargs)

def get(*args, **kwargs):
    return Action.get(*args, **kwargs)

def put(*args, **kwargs):
    return Action.put(*args, **kwargs)

def display(*args, **kwargs):
    return Action.display(*args, **kwargs)

def action(actionf):
    actionf.detcord_action = True
    return actionf
