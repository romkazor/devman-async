# Microservice for archivate files

The microservice creating archive on the fly by request from the user.


## How to install

You need Python version 3.6 and higter.

```
pip install -r requirements.txt
```


## How to use

You can use this arguments:


```
--help, -h: Show help message
--log:   On/off logging
--delay: Set delay for response in seconds (float)
--dir:   Set directory of photos, default "/tmp/photos"
--port:  Set server port, default 8080
--size:  Set chunk size in KB, default 100 KB
```
Example:

```
python3 server.py --delay 0.1 --dir /tmp/photos --port 8080 --log
```

Then server will start on port 8080, to check this go to the browser on the page http://0.0.0.0:8080/
