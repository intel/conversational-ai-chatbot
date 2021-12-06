# Login

- [Login](#login)

To use the chatbot, we need the credentials of openbanking server. For this demo, [create credentials here](https://apisandbox.openbankproject.com/consumer-registration ). There are two ways to login.

**For development**:
  - We can update the credentials in compose file. We need to set env `DEVELOPMENT=1`

  ```yml

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

**For Usage**:
  - Authz component asks for credentials via stdin. We can run the chatbot and then attach to the authz component to enter credentials.
    Enter username, password, apikey one after another.

```
   docker attach chat_authz_1

   # now enter username <ENTER>
   # password <ENTER>
   # apikey   <ENTER>

   ## Then use ctrl-p, ctrl-q  sequence to detach, without exiting
```