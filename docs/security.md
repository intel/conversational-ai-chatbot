# Security Design

- [Security Design](#security-design)
	- [Security Guide](#security-guide)
		- [Secure configuration](#secure-configuration)
		- [Security Capabilities, parameters and settings](#security-capabilities-parameters-and-settings)
		- [Privacy Policy and type of data handled.](#privacy-policy-and-type-of-data-handled)
		- [Authentication and authorization Mechanisms](#authentication-and-authorization-mechanisms)
		- [Data Protection Mechanisms (at rest and in transit)](#data-protection-mechanisms-at-rest-and-in-transit)
		- [Logging](#logging)
		- [Physical Security](#physical-security)

This software is a conversational AI application for a demo banking usecase. In simple language, the user can talk to the application, by speaking to it and the application answers the queries in a DL based human like voice. 

The different components of the application are deployed as `services` on docker swarm. The application is designed as a pipeline of components i.e services, which use publish-subscribe pattern for data flow using 0MQ networking library. The services run as containers thus fully isolated from the outside environment.

The communication between services `Audio Ingestion Service`, `NLP Service`, `ASR Service` and `TTS Service` uses *unix domain sockets*, which are file system based, and are mounted into docker containers of the services using *a shared docker volume*. The communication between `services` via 0MQ is not encrypted, but the sockets are protected via user permissions of Linux. Only a admin/root user can access them outside of containers. 

The chatbot responsibiltiy of the software is delegated to `RASA Action Service` container which uses [RASA framework](https://rasa.com/) to perform NLU tasks and call banking api via `obp_api` component. `obp_api` is a client library to connect to openbankproject server. It is found in `<repo-root>/nlp/obp_api`. `RASA Action Service` is a REST api server which support JWT Authentication with key size 32bytes and jwt algorithm=HS256. `NLP Service` connects to other components via 0MQ library and unix sockets, however it connects to `RASA Action Service` via `https`. The TLS Keys used for `https` are RSA 3072 and stored in docker secrets.

Session management is managed by `Authz Service`. It is the single point of authentication of user. Credentials are not stored in any container. Authentication and authorization is performed by openbankproject server, via `https` calls. So, this software uses a third party, web server which is hosted elsewhere to authenticate the users. `Authz Service` gets the `jwt token` from openbankiproject server and creates a unique session-id for the user. This `login-session` is valid for 15 minutes. `Authz Service` publishes the session-id on 0MQ. `Audio Ingestion Service` subscribes to the `Authz Service` and recieves the `session-id`. The `session-id` is propagated along the pipeline with data. Each of the `NLP Service`, `ASR Service` and `TTS Service` can connect to `Authz` via 0MQ RPC call to verify the session-id. The data is recieved only when session-id is valid i.e the user is still logged in. `Authz` hosts RPC Servers for commands such as `verify_token`, `get_token` and `logout_token`. Only `RASA Action Service` uses RPC calls `get_token` and `logout_token`, while other containers use `verify_token` RPC call.

## Security Guide

The basic interaction of the user with the software is via speech. User needs to give instructions to the software by speaking and the software processes the instructions and speaks the output back to the user, using `tts service`. Only other interaction with the software is via `authz service` where user needs to enter the open bankking server credentials. Credentials need to be entered once at the start of the application run. Login Session expires after 15 minutes, so after every 15 minutes of use, software will time out and ask for credentials again.

### Secure configuration

The software consists of services which run as containers on a single node docker swarm. Data to be protected (i.e TLS keys and jwt secrets/algo etc) are kept in docker secrets. Configurations like input/output ports are set via environment variables in the stack/compose yml file.

The software is represented using compose and stack yml files. It is split into frontend and backend. 

_Frontend houses the services (`audio ingestion`/ `tts`) which need to access the audio hardware for recording and playback. They are run using docker compose and do not have acess to docker swam or docker secrets._

_Backend houses `authz`, `asr`, `nlp`, `rasa action server` services which run on docker swarm and have access to docker secrets. They have no access to hardware device files/nodes._

```
- docker-compose-backend.yml
- docker-compose-frontend-respeaker.yml
```
The `docker-compose-backend.yml` runs the services via docker stack and uses docker secrets for keys. Docker secrets can only be used in this compose. 

However `docker-compose-frontend-respeaker.yml` runs `audio ingestion service` and `tts service` which need access to audio hardware for recording and playback 

### Security Capabilities, parameters and settings

Software supports a single user at a time. The script `create_secrets.sh` is used to create all required keys and secret data and save them as docker secrets for use in the docker swarm.

### Privacy Policy and type of data handled.

Software does not store any data from the user. The speech input from the user is not stored on device or cloud.

### Authentication and authorization Mechanisms

The `authz service` handles the user authentication. Software relies on [openbankproject server credentials](https://apisandbox.openbankproject.com/consumer-registration) for login. 

Additionally, `rasa action service` uses JWT for authentication and expects it in Bearer token format in the https request headers. `nlp service` acts as a client for `rasa action service` and creates a `jwt` based on secret and jwt algorithm. The jwt secret and algorithm are stored as docker secrets. 

### Data Protection Mechanisms (at rest and in transit)

The Software doesn't store any user data on disk or in data base. The secure data like TLS keys and JWT secrets are stored as docker secrets. Models and configs are stored inside docker images and require root privilege to access. Software runs containers which have user privileges and do not access host file system. `nlp` and `rasa action service` which handle the sensitive data are network isolated using docker networks. `nlp` connects to `rasa action server` over https secure channel authenticated using JWT. A new JWT is created for each request and expires in 20 seconds.

All services containers transmit data over an __unencrypted 0MQ channel__. They use file based unix sockets, housed in a shared docker volume, to send and recieve data. All containers run with user permissions. The user created in containers is different from the other users on the same machine. Since the sockets are kept in a shared docker volume and created with  specific user permissions, only container services or root admin can access them. Hence the software is secure from other users of the machine but root admin can still access the secrets and the sockets. *So the system is protected against authorized user access but not against malicious admin access.*  

NOTE: The system is not protected against adversarial machine learning attacks against ASR and NLP.

### Logging

The logs are written to stdout/stderr of the docker containers. `docker service logs` can be used to check the logs for each service.

### Physical Security

The software is intended for a kiosk like machine which serves one user at a time. The system integrator should take care of this aspect. Only authorized admin should have root access.