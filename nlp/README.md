# NLP Service


It is a Natural Language Service which interfaces with a RASA&trade; chatbot server. It can read text input coming from 0MQ on a predefined topic and send it to [RASA&trade;](https://rasa.com/) api server running locally on in another docker container. It can publish the replies from RASA&trade; to 0MQ on predefined topic.

The source is kept in `<repo-root>/nlp/app`
## Pre-requisites

- docker
- 0MQ

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (unicode string) | bytes (unicode string) |

NOTE: A string can be obtained from byte encoded input/out buffer using `.decode()` method. `data_string = data.decode()`

## `RASA ACTION` Container Image Components

RASA&trade; based api server and action server run as a single docker container. The containeris  referred to as `rasa action service`.


`rasa action service` has the following components:
- `rasa api server`: This has nlu and nlg models. It is bound to localhost. source is in `<repo-root>/nlp/rasa_api_server`.
- `rasa action server`:  This has actions for getting information from backend server. This is bound to localhost. Source is in `<repo-root>/nlp/rasa_action_server/src`
- `obp_api`: library to connect to backend openbanking server, used by `rasa action server`. Source is in `<repo-root>/nlp/obp_api`
- `nlp_server`: This is the proxy to `rasa api server` and provides `JWT` authentication. It is bound to `0.0.0.0:8000`. Source is in `<repo-root>/nlp/nlp_server`

The `nlp service` can give https POST calls to `rasa action service` vial URL `https://rasa_action:8000` using hostname resolution provided by docker.

## Sample `NLP Service`

```yml
  nlp_app:
    image: "nlp_app:1.0"
    hostname: nlp_app
    environment:
      - INPUT_ADDR=ipc:///feeds/1
      - INPUT_TOPIC=text
      - OUTPUT_ADDR=ipc:///feeds/2
      - AUTHZ_SERVER_ADDR=ipc:///feeds/9
      - OUTPUT_TOPIC=nlp
      - LOG_LEVEL=debug
      - JWT_SECRET=jwtsecret
      - TLS_CERT=nlp_tls_cert
      - TLS_KEY=nlp_tls_key
    command: ["python3", "/app/main.py"]
    secrets:
      - nlp_tls_cert
      - nlp_tls_key
      - jwtsecret
    volumes:
      - zmq_ipc_vol:/feeds
    depends_on:
     - rasa_action

```

## Sample `RASA ACTION SERVICE`

```yml

rasa_action:
    image: "action_server:1.0"
    hostname: rasa_action
    environment:
      - SANIC_JWTSECRET=jwtsecret
      - SANIC_JWTALGORITHM=jwtalgo
      - TOKEN_SERVER_ADDR=ipc:///feeds/19
      - SANIC_TLS_CERT=rasaw_tls_cert
      - SANIC_TLS_KEY=rasaw_tls_key
      - SANIC_SERVERCERT=rasaw_tls_cert
      - SANIC_SERVERKEY=rasaw_tls_key
      - ACTION_TLS_CERT=action_tls_cert
      - ACTION_TLS_KEY=action_tls_key
      - API_TLS_CERT=/run/secrets/api_tls_cert
      - API_TLS_KEY=/run/secrets/api_tls_key
    volumes:
      - zmq_ipc_vol:/feeds
    secrets:
      - rasaw_tls_cert
      - rasaw_tls_key
      - api_tls_cert
      - api_tls_key
      - action_tls_cert
      - action_tls_key
      - jwtsecret
      - jwtalgo

```

## `nlp service` and `rasa action service` authentication

`nlp service` connects to `rasa action service`. The `rasa action service` supports `JWT` authentication. The jwtsecret and jwtalgorithm has to be provided to `rasa action service` via docker secrets i.e. It should be mapped to `/run/secrets` path. We need to set env variable `SANIC_JWTSECRET` for jwtsecret and env variable `SANIC_JWTALGORITHM` for jwtalgorithm.

The env variable  `SANIC_JWTALGORITHM` should be the name of docker secret. Its value should be 'HS256'.

The env variable `SANIC_JWTSECRET` should be the name of docker secret. Its value should be a 32 byte string.


## Creating Docker secrets for `nlp service`

1. Create JWT Secrets
   - Create a random 32 byte string to be used as a secret.
     ```
     echo "some32bytestring" | docker secret create jwtsecret -
     # Then value of env var should be
     JWT_SECRET=jwtsecret
     ```
2. Create TLS Keys
   - Create RSA TLS Keys and Certs with size 3072.
   - Convert the keys to docker secrets
   - update the env vars with docker secret names
   - These are required variables to be updated
      ```
      TLS_CERT=nlp_tls_cert
      TLS_KEY=nlp_tls_key
      ```

## Creating docker secrets for `rasa action service`

1. Create JWT Secrets
   - Create a random 32 byte string to be used as a secret.
     ```
     echo "some32bytestring" | docker secret create jwtsecret -
     # Then value of env var should be
     SANIC_JWTSECRET=jwtsecret
     ```
   - Create jwtalgorithm secret
     ```
     echo "HS256" | docker secret createjwtalgo -

     # Then the value of env var would be
     SANIC_JWTALGORITHM=jwtalgo
     ```
2. Create TLS Keys
   - Create RSA TLS Keys and Certs with size 3072.
   - Convert the keys to docker secrets
   - update the env vars with docker secret names
   - These are required variables to be updated
      ```
        SANIC_SERVERCERT=rasaw_tls_cert
        SANIC_SERVERKEY=rasaw_tls_key
        ACTION_TLS_CERT=action_tls_cert
        ACTION_TLS_KEY=action_tls_key
      ```
## Limitations

- Responses are limited by training data used for RASA&trade; chatbot.
- It supports English Language only.
- `obp_api` doesn't support all api(s).
- Rasa 1.x generates at times different model with the same input training data
