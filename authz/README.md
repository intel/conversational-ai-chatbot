# Authz Service

It handles the user-login part of the application. It is reponsible for session creation, management and verification. The user needs to have credentials for openbankproject server.
For this demo, [create credentials here](https://apisandbox.openbankproject.com/consumer-registration ).

It hosts functionality to *create-session, publish session-id, verify session-id and get obp jwt token*. Those functionalities are accessible over different sockets/ports.

*Verify Session ID:*
How the client should avail this feature.


Easy Way
```
INPUT_ADDR = .. # depends on which component to connect
AUTHZ_RPC_SERVER_ADDR = .. # check env var SESSION_ADDR passed to authz

from zmq_integration_lib import get_inpad
ip = get_inpad(INPUT_ADDR, INPUT_TOPIC, AUTHZ_RPC_SERVER_ADDR)
for d,e in ip.data_and_event_generator():
    print (d)

```

*Direct way*

```
session-id = ... # Got from some component
import zmq_integration_lib as z
c=z.RPCClient(AUTHZ_RPC_SERVER_ADDR, z.supported_cmds)
c.verify(session_id)

```



*Get Token:*

This is solely used by `rasa actions service` to get the token. The token is then used to retireve the information from banking servers.

```

import zmq_integration_lib as z
c=z.RPCClient(AUTHZ_RPC_SERVER_ADDR, z.supported_cmds)
c.get_token()

```

*Publish Session id*

`Authz` publishes `session-id` and `event` periodically. `event` can be `signin`. Only the first component in the pipeline needs to do this. Here audio ingestion needs to do this.


```python
import zmq_integration_lib as z
ips = z.InputPortWIthEvents(authz_output_addr, authz_output_topic)
for id, event in ips.input_port.data_and_event_generator():
            if event == 'signin':
               self._session_valid = True
               self._session_id =  id
```
### Logout Token

This is solely used by `rasa action service` to logout the session. This rpc call makes Authz` delete the session-id and ask for login again.

```python

import zmq_integration_lib as z
c=z.RPCClient(AUTHZ_RPC_SERVER_ADDR, z.supported_cmds)
c.logout('sometoken')


```



NOTE: The logout rpc doesn't invalidate the jwt token from open bankproject server. This is a [limitation of openbankproject server as of now](#limitations).

## For development

Set these env variables and run authz. In DEVELOPMENT mode, credentials can be passed via env vars. This is not possible in production mode.

```
set TOKEN_SERVER_ADDR=tcp://*:6901
set OUTPUT_ADDR=tcp://*:6700
set OUTPUT_TOPIC=userloggedin
set SESSION_ADDR=tcp://*:6900
set DEVELOPMENT=1
set D_USERNAME=...
set D_PASS=...
set D_APIKEY=...
set D_TOKEN=...
set LOG_LEVEL=debug
python main.py
```

## Pre-requisites
- 0MQ
- python3

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| No Input | bytes (unicode string) |



##

| ENV Variable  | Description       |
| ------------- | --------------------- |
| INPUT_ADDR | It is the address of 0MQ socket. |
| INPUT_TOPIC | It is the topic on which 0MQ input is recieved. |
| OUTPUT_ADDR |It is 0MQ socket address on which wave data is published. |
| OUTPUT_TOPIC | It is the topic on which tts service will publish pcm wave data. |
| TOKEN_SERVER_ADDR | It is the address of 0MQ socket of rpc server which server get_token and logout apis. |
| SESSION_ADDR | It is the address of 0MQ socket of rpc server which serves verify api. |
| TLS_CERT | It is the name of a docker secret which has TLS cert. |
| TLS_KEY | It is the docker secret which has TLS key. |
| DEVELOPMENT | It is needed only while development. Enables getting login creds from env variables |
| LOG_LEVEL | It can have values info, debug, warning, error. |


## Login

To use the chatbot, we need the credentials of openbanking server. There are two ways to login.

**For development**:
  - We can update the credentials in compose file. We need to set env `DEVELOPMENT=1`

  ```

  authz:
    image: "authz:${TAG}"
    network_mode: host
    environment:
      - TOKEN_SERVER_ADDR=ipc:///feeds/19
      - OUTPUT_ADDR=ipc:///feeds/11
      - OUTPUT_TOPIC=userloggedin
      - SESSION_ADDR=ipc:///feeds/9
      - DEVELOPMENT=1
      - D_USERNAME=<add username here>
      - D_PASS=<add obp pass here>
      - D_APIKEY=<add obp key here>
      - D_TOKEN=<optionally may add token here>
      - LOG_LEVEL=debug
    command: ["python3", "/app/main.py"]
    #tty: true
    #stdin_open: true
    volumes:
      - zmq_ipc_vol:/feeds
    depends_on:
      - audio_ingestion


  ```

**For production**:
  - Authz component asks for credentials via stdin. We can run the chatbot and then attach to the authz component to enter credentials.
    Enter username, password, apikey one after another.

```
   docker attach chat_authz_1

   # now enter username <ENTER>
   # password <ENTER>
   # apikey   <ENTER>
```

## Limitations

- Logout doesn't invalidate the token. [Issue](https://github.com/OpenBankProject/OBP-API/issues/1865)