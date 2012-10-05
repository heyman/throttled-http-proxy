from gevent import monkey
monkey.patch_all()

import sys
import ssl
import gevent
import socket
from gevent.coros import BoundedSemaphore
from gevent.pywsgi import WSGIServer
from optparse import OptionParser
from paste.proxy import TransparentProxy

from log import setup_logging
from logging import getLogger

"""
def test_server():
    def app(environ, start_response):
        gevent.sleep(10)
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n']
    
    s = WSGIServer(("0.0.0.0", 6566), app)
    s.serve_forever()
g = gevent.spawn(test_server)
"""

# set socket timeout to 60 seconds
socket.setdefaulttimeout(60.0)

class WsgiThrottler(object):
    def __init__(self, application, pool_size):
        self.application = application
        self.semaphore = BoundedSemaphore(pool_size)
    
    def __call__(self, environ, start_response):
        with self.semaphore:
            return self.application(environ, start_response)

def parse_options():
    parser = OptionParser(usage="main.py [options] target-host")
    parser.add_option(
        '-i', '--interface',
        dest="interface",
        default="0.0.0.0",
        help="What interface to listen to. Defaults to 0.0.0.0"
    )
    parser.add_option(
        '-p', '--port',
        dest="port",
        type="int",
        default=6565,
        help="What port to listen on. Defaults to 6565"
    )
    parser.add_option(
        '--certfile',
        dest="certfile",
        help="SSL certfile if the proxy server should use SSL"
    )
    parser.add_option(
        '--keyfile',
        dest="keyfile",
        help="SSL keyfile if the proxy server should use SSL"
    )
    parser.add_option(
        '--logfile',
        dest="logfile",
        help="File to log to. If not specified, logging will go to stdout"
    )
    parser.add_option(
        '--loglevel',
        dest="loglevel",
        default="INFO",
        help="Log level. Defaults to INFO"
    )
    parser.add_option(
        "--pool-size",
        dest="pool_size",
        type="int",
        default=1,
        help="Number of concurrent requests that can be proxied",
    )
    
    opts, args = parser.parse_args()
    return parser, opts, args

def main():
    parser, options, arguments = parse_options()
    if not arguments:
        parser.print_help()
        return
    
    # configure logging
    setup_logging(options.loglevel, options.logfile)
    
    proxy = TransparentProxy(arguments[0])
    throttler = WsgiThrottler(proxy, options.pool_size)
    
    # SSL settings
    ssl_settings = {"certfile": options.certfile, "keyfile": options.keyfile}
    
    main_logger = getLogger(__name__)
    main_logger.info("Proxying %s on %s:%i with a maximum of %i concurrent requests" %(
        arguments[0],
        options.interface,
        options.port,
        options.pool_size,
    ))
    
    server = WSGIServer((options.interface, options.port), throttler, log=sys.stdout, **ssl_settings)
    server.serve_forever()

if __name__ == "__main__":
    main()
