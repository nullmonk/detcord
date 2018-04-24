# detcord
deployment + autopwn for linux and eventually windows


## About
`detcord` allows for simplified deployment of redteam scripts and binaries.
Currently detcord supports running `detfile.py` actions against the specified hosts, however, future
implementations will allow running detcord as a server. The server functionality will provide
auto-registering of hosts, autopwn capabilities, and perhaps credential bruteforcing.


Influenced heavily from [fabric](https://github.com/fabric/fabric). I initially used this framework
for my deployment but quickly wanted to make it a little more lightweight and specific to what I
wanted to do. In addition, fabric did not support Python 3+ and did not allow for certain type of
actions to be run against a host.


## Usage
Usage is fairly simple for running basic functions against a host. Create a `detfile.py` and import
the actions that you will need for your deployment. In addition to each action, you will need to
import the `action` decorator
```python
# detfile.py
from detcord.actions import action, run
```

Set up a simple environment for the detfile. Currently the environment supports the following values

| Key          | Description                                                                  |
|--------------|------------------------------------------------------------------------------|
| hosts        | An array of hosts to run the actions against. Must be specified              |
| user         | The username to use on each host                                             |
| pass         | The password to use on each host                                             |
| current_host | The current host that is being run on. Can be called from an action function |

```python
env = {}
env['hosts'] = ['192.168.1.2', '192.168.1.3']
env['user'] = 'root'
env['pass'] = 'toor'
```

You may now write a simple function to run against a host
```python
@action
def HelloWorld():
    ret = run("whoami")
    print(ret['stdout'])
```
