"""
detcord : Action execution on hosts

Micah Martin - knif3
"""

from detcord import action, display

env = {}  # pylint: disable=invalid-name
env["user"] = "root"
env["pass"] = "toor"
env["hosts"] = ["localhost"]
env["threading"] = False  # threading defaults to false


@action
def test(host):
    """
    A test action for the detcord project

    Showcases the commands that can be run
    """
    # You can run simple commands
    ret = host.run("echo welcome to detcord")
    # You can pass a script to be piped into the process
    ret = host.run("bash", "echo this is valid\nThis is an error\n")
    # You can run a command as root
    ret = host.run("whoami", sudo=True)
    # Display will print the results nicely
    display(ret)
    # Run commands locally
    ret = host.local("whoami")
    # Display can handle output to a file object, or any kwarg that print
    # can handle
    with open("/tmp/detcord_log.txt", "a") as outfile:
        display(ret, file=outfile)

    # Put and push files to/from the server
    try:
        host.put("README.md", "/tmp/README")
    except PermissionError as _:
        # Catch a permission denied error and try again as root
        host.put("README.md", "/tmp/README", sudo=True)

    host.get("/tmp/README", "test.swp")

    # Get information about the commands run
    ret = host.run("not_a_real_command")
    if ret.get("status", 1) != 0:
        print("Command failed to run!")


def support_action():
    """
    This function is not a detfile action and cannot be called with det
    """
    pass
