## Configuration
- [Configuration](#configuration)
	- [Using recorded audio](#using-recorded-audio)
	- [Recording from Microphone](#recording-from-microphone)

Before using the software, we assume that we have an openbanking server running. For demo purposes we can connect to a server hosted by openbankproject or run a local version of the server. The instructions are detailed in `nlp/obp_api/README.md`. Follow the instructions and create the credentials. For this demo, [create credentials here](https://apisandbox.openbankproject.com/consumer-registration ). Note down the `username`, `password` and the `apikey`.

### Using recorded audio
*Using pre-recorded audio files*

- This method is useful when developing and debugging. When developing/debugging on a remote machine, this is the preferable method.


### Recording from Microphone

- This is a practical method to use the application. We need a microphone/micorphone array connected to the machine. We can talk to the application using `WAKE_WORD`.

The list of supported wake words is 
- chatbot
- respeaker

We can configure the WAKE_WORD in `compose/docker-compose-frontend-respeaker.yml` via an environemnt variable.

It supports banking queries. Example usage:

```
<user>: Respeaker
<user>: Good Morning
<chatbot>: <Some reply from the chatbto>
<user>: Show me the list of available banks.
<chatbot>: <chatbot speaks out some information>
```

NOTE: This software uses the open banking server hosted at URL "https://apisandbox.openbankproject.com" for demonstartion purposes. It is possible to run the open bank server at a differnt location locally or on cloud. To enable that we need to edit URL of openbankproject server in the following locations.

- `<repo-root>/authz/obp_helper.py` :*_prepare_login_config()*
- `<repo-root>/nlp/rasa_action_server/src/actions.py` : *backend_helper()*
