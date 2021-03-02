# Async chat client for minechat
- Connect to service minechat.dvmn.org
- Sending messages
- Logging messages
- Other

## Examples:

### Read chat:

Optional:
- `--host` - hostname or ip chat, default: minechat.dvmn.org
- `--port` - port chat, default: 5000
- `--history` - logfile to save chat history, default: minechat.history

```
python3 chat_reader.py --host minechat.dvmn.org --port 5000 --history minechat.history
```
or
```
python3 chat_reader.py
```

### Write to chat:
Required
- `--message` message to send

Optional:
- `--host` - hostname or ip chat, default: minechat.dvmn.org
- `--port` - port chat, default: 5050
- `--key` - key, default: check in key file
- `--register` - register new user, default: False
- `--username` - username of new registered user
    
```
python3 chat_writer.py --message 'Hello World'
```
