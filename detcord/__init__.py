from .manager import Manager

def action(actionf):
    actionf.detcord_action = True
    return actionf

MainManager = Manager()
