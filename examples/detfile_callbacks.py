"""
detcord : Action execution on hosts

Micah Martin - knif3
"""

from detcord import action, display

env = {}  # pylint: disable=invalid-name
env["user"] = "root"
env["pass"] = "toor"
env["hosts"] = ["localhost"]
env["silent"] = False  # Dont suppress output from the actions
env["threading"] = False  # threading defaults to false


def on_detcord_begin(detfile="", hosts=[], actions=[], threading=False):
    print("Detcord has been launched. {}".format(actions))


def on_detcord_action(host="", action="", return_value=None):
    print(
        "Detcord action '{}' has been run on {}. return value? {}".format(
            action, host, bool(return_value)
        )
    )


def on_detcord_action_fail(host="", action="", exception=None):
    print(
        "Detcord action '{}' has failed for {}. Exception: {} ({})".format(
            action, host, exception, type(exception)
        )
    )


def on_detcord_end(detfile=""):
    print("Detcord has ended :(", detfile)


@action
def test(host):
    """
    A test action for the detcord project

    Showcases the commands that can be run
    """
    display(host.local("whoami"))


@action
def test2(host):
    raise Exception("This action will fail")


def support_action():
    """
    This function is not a detfile action and cannot be called with det
    """
    pass
