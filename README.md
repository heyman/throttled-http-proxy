# Throttled HTTP Proxy

Small server that transparently proxies HTTP requests to some other pre-defined server. 
The number of requests can be throttled, which may be useful when using an API
which imposes limits on the number of concurrent requests that you are allowed to make.

## Usage

```
Usage: main.py [options] target-host

Options:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface=INTERFACE
                        What interface to listen to. Defaults to 0.0.0.0
  -p PORT, --port=PORT  What port to listen on. Defaults to 6565
  --certfile=CERTFILE   SSL certfile if the proxy server should use SSL
  --keyfile=KEYFILE     SSL keyfile if the proxy server should use SSL
  --logfile=LOGFILE     File to log to. If not specified, logging will go to
                        stdout
  --loglevel=LOGLEVEL   Log level. Defaults to INFO
  --pool-size=POOL_SIZE
                        Number of concurrent requests that can be proxied
```
