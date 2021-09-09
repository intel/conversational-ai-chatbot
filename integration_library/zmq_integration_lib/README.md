# zmq_integration_lib

It is a python package for ipc communication between different processes. It is based on 0MQ sockets. It supports asynchronous publish subscibe mode called `streaming mode` and a synchronous request reply mode called `rpc mode`. Additionally it has a modified `streaming mode` which is called `session sware streaming mode`.


## Pre-requisites

- python3
- 0MQ

## Install



```
# need to install libzmq via apt-get/dnf etc
$ pip3 install -r requirements
$ python setup.py install
or
$ pip3 install .
```

_For development use virtualenv to install and test it._


## Usage

### Streaming Usecase

It uses publish-subscibe design pattern to decouple receivers from senders. It supports two streaming socket interfaces called ports.

`OutputPort` is a streaming output port which can publish any data on a specific address and a specific topic.

It suports pushing a message called `event` along with the data. Pushing an `event` is optional but any string can be sent as an `event`.

*Publishing data to zmq/0mq*
```python
from zmq_integration_lib import OutputPort
op = OutputPort(addr="tcp://*:5555",
                topic="asr")

for data in some_list:
    op.push(data)
# any event can be sent as second param to push method.
op.push(b'', 'EOS')

```

`InputPort` is a streaming input interface from which we can recive data which is published using an `OutPutPort`. We need to provide `address` and `topic` on which data is being published. `InputPort` provides a python data generator function which can be iterated upon to receive data.

*Receiving data from 0MQ publisher.*

```python
from zmq_integration_lib import InputPort

ip = InputPort(addr="tcp://localhost:5555", 
               topic="asr")
for data, event in ip.data_and_event_generator():
    do_something(data)

```


### RPC Usecase

It is possible to run a rpc server and client using this package.`rpc.py` has a dict `supported_cmds`, which has the list of supported remote procedure calls. It uses `jsonrpc-2.0` over 0mq req-rep sockets. Currently it supports only three rpc calls. However rpc calls can be extended via `supported_cmds` in `rpc.py`:
- get_token()
- logout(token)
- verify_token(token)

*RPC Server*
```
>>> def verify(sha):
        return True
>>> import zmq_integration_lib as z
>>> r=z.RPCServer('tcp://*:6900', z.supported_cmds)
>>> r.set_handler('verify', verify)
>>> r.run()
```
*RPC Client*

```
>>> import zmq_integration_lib as z
>>> c=z.RPCClient('tcp://localhost:6900', z.supported_cmds)
>>> c.verify('sometext')
```

### Streaming Usecase with Session verification

In the conversationa AI usecase, we need to verify a session_id, which comes as part of data, when using the treaming mode `session_aware in/outpads`. To verify the session_id, we need address of a `rpc` server hosting the verify method. So we have another set of session sware streaming interfaces, which handle the rpc calls internally and abstract away the deatils from the user and provide an interface, which is compatible with normal `streaming mode`. These are called `streaming inpad`  and `streaming outpad`. The only difference is that we have an additional paramter while creating inpad and outpad. This parameter is the address of an `rpc server` which hosts the `verify_token()` rpc method implementation.

*Receiver*

```python
from zmq_integration_lib import get_inpad
input_addr = 'tcp://localhost:6000'
input_topic = 'hello'
rpc_server_addr = 'tcp://localhost:6900'
ip = get_inpad(input_addr, input_topic, rpc_server_addr)
for data,event in ip.data_and_event_generator():
    print (d)
```

*First Sender (with no inpad)*

```python
from zmq_integration_lib import get_outpad
sid = '4a501b51317e2c8f4a0fd7831d3e09dc'
op = get_outpad("tcp://*:6000", "hello")
op.update_session_id(sid)
op.push(b'Hi boy')
```

*Subsequent Senders (apps which ahve both inpad and outpad)
 no explicit session id is required, it is handled internally by the module*

```python
from zmq_integration_lib.session_aware import get_outpad
op = get_outpad("tcp://*:6000", "hello")
op.push(b'Hi boy')
```


## Test

```sh
cd test
python -m unittest discover
```

## Limitations

- Output streaming ports take binary data. String can be converted to bytes via utf8 encoding. For other data structures serialisation would be needed.
- For streaming input ports, the data generators block on read. So they can be run in a different thread.
