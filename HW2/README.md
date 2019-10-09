# Georgetown-Network-Security
My project and assignment for Georgetown Course - Network Security

Author: Zhao Jin

## How to run

### encryptIMserver.py
Use this command:
```
python encryptIMserver.py -p port
```

port: the port you want your server to listen on

### encryptIMclient.py

Use this command:
```
python encryptIMclient.py -p port -n username -s server_address -a authenticationKey -c confidencialityKey
```
port: the port you want your server to listen on

username: your nickname which will show in others' window along to message you send

address: IP address or hostname of the server you want to connect to

authenticationKey: the key you use to verify yourself

confidencialityKey: the key you use to encrypt your message

