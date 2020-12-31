import http.server
import socketserver


# https://stackoverflow.com/questions/39801718/
def handler_from(directory):
    def _init(self, *args, **kwargs):
        return http.server.SimpleHTTPRequestHandler.__init__(self, *args, directory=self.directory, **kwargs)
    return type(f'HandlerFrom<{directory}>',
                (http.server.SimpleHTTPRequestHandler,),
                {'__init__': _init, 'directory': directory})


def serve(args, config):

    rootdir = config['DIR_PUBLISH']
    port = config['SERVER_PORT']
    httpd = socketserver.TCPServer(("localhost", port), handler_from(rootdir))
    print("Starting server at: http://localhost:{}/".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Stopping server.")
    httpd.server_close()
