# obp_api

It is a client sdk/library to connect to [openbankingproject](https://www.openbankproject.com/) api server. It is possible to use this library to connect to a server hosted at `https://apisandbox.openbankproject.com`. The server can however be run locally also after following instructions from [openbanking api github]( https://github.com/OpenBankProject/OBP-API.git) repo.

This component has a library which is extensible to support all endpoints of obp api server. The `accounts.py` implements a class to support accounts obp api. Similarly all apis will be supported by extending `base.py` which handles all http request infrastructure. The api supported and to be supported is [here](https://apiexplorersandbox.openbankproject.com/)

## Pre-Requisites

- python3
- a running openbanking server instance
- openbanking server credentials.

## Install

```bash
$ python setup.py install
or
$ pip3 install .
```


## Config for Login

The library support `config.yml` in the following format. It can be a file or a string in the memory.

```yaml
credentials:
  URL: https://apisandbox.openbankproject.com
  API: v4.0.0
  username: someusernamehere
  password: somepasswordhere
  consumer_key: mthisisatokehgdogqhba22lp2dfbs3qg5rmutx2

```

### `config.yml` as a file
Create a file `config.yml` with the data above.

```python

from obp_api import base

config_file = 'config.yml'
connection_helper = base.Connector(config_file)
connection_helper.login()


```

### `config.yml` as an in memory string

```python

from obp_api import base
import io
import yaml

def _prepare_login_config(user, pwd, apikey):

    yaml_str = '''credentials:
  URL: https://apisandbox.openbankproject.com
  API: v4.0.0
  username:
  password:
  consumer_key:
    '''
    data = yaml.safe_load(yaml_str)
    data['credentials']['username'] = user
    data['credentials']['password'] =  pwd
    data['credentials']['consumer_key'] = apikey
    configyam = io.StringIO()
    yaml.dump(data, configyam)
    return io.StringIO(configyam.getvalue())


config_file = _prepare_login_config('someuser', 'somepass', 'someapikey')
connection_helper = base.Connector(config_file)
connection_helper.login()

```


## Run Example

```
# create a config for credentials as `config.yml`
cd examples
python list_banks.py -c config.yml
```

## Limitations

- It is not exhaustive, all apis are not implemented.
- Only `Direct Login` is supported.
