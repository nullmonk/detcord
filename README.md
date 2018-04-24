# detcord
deployment + autopwn for linux and eventually windows

## About
`detcord` allows for simplified deployment of redteam scripts and binaries.
Currently detcord supports running `detfile.py` actions against the specified hosts, however, future
implementations will allow running detcord as a server. The server functionality will provide
auto-registering of hosts, autopwn capabilities, and perhaps credential bruteforcing.


Influenced heavily from [fabric](https://github.com/fabric/fabric). I initially used the fabric framework
for my deployment but quickly wanted to make it a little more lightweight and specific to what I
wanted to do. In addition, fabric did not support Python 3+ and did not allow for certain type of
actions to be run against a host.

> Lots of improvements will be made to this tool over time. Ii will try to keep the `master` branch
> stable but occasionally errors may occur

## Usage
Usage is fairly simple for running basic functions against a host. Create a `detfile.py` and import
the actions that you will need for your deployment. In addition to each action, you will need to
import the `action` decorator
```python
from detcord.commands import action, run, display
```

Set up a simple environment for the detfile. Currently the environment supports the following values

| Key          | Required | Description                                       |
|--------------|----------|---------------------------------------------------|
| hosts        | Yes      | An array of hosts to run the actions against.     |
| user         | Yes      | The username to use on each host                  |
| pass         | Yes      | The password to use on each host                  |
| current_host | No       | The current host that the action is being run on. |

```python
env = {}
env['hosts'] = ['192.168.1.2', '192.168.1.3']
env['user'] = 'root'
env['pass'] = 'toor'
```

You may now write a simple function to run against a host.
```python
@action
def HelloWorld():
    '''
    This is a Hello World action
    '''
    ret = run("whoami")
    display(ret)
```

To run your detfile, simply call det from the command line with the action you would like to run
```
det HelloWorld
```

To list all the actions in a detfile, run the det command without any arguments. The first line of
the function docstring is used as the description.


## Actions
Currently the following commands can be imported and run from a detfile

| Function | Args                  | Description                                               |
|----------|-----------------------|-----------------------------------------------------------|
| run      | command               | Run `command` against the remote host                     |
| script   | command, stdin        | Run `command` against the remote host and pass in `stdin` |
| local    | command               | Run `command` on the local machine                        |
| put      | localfile, remotefile | Save `localfile` on the remote host to `remotefile`       |
| get      | remotefile, localfile | Save `remotefile` from the remote host into `localfile`   |
| display  | retval                | Pretty print the return value of these actions            |
