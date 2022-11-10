from __future__ import print_function
import json
import re
import threading
import io

JSON_RPC_REQ_FORMAT = "Content-Length: {json_string_len}\r\n\r\n{json_string}"
LEN_HEADER = "Content-Length: "
TYPE_HEADER = "Content-Type: "


# TODO: add content-type


class MyEncoder(json.JSONEncoder): 
    """
    Encodes an object in JSON
    """
    def default(self, o): # pylint: disable=E0202
        return o.__dict__ 


class JsonRpcEndpoint(object):
    '''
    Thread safe JSON RPC endpoint implementation. Responsible to recieve and send JSON RPC messages, as described in the
    protocol. More information can be found: https://www.jsonrpc.org/
    '''
    def __init__(self, stdin, stdout):
        self.stdin = stdin
        self.stdout = stdout
        self.read_lock = threading.Lock() 
        self.write_lock = threading.Lock() 

    @staticmethod
    def __add_header(json_string):
        '''
        Adds a header for the given json string
        
        :param str json_string: The string
        :return: the string with the header
        '''
        return JSON_RPC_REQ_FORMAT.format(json_string_len=len(json_string), json_string=json_string)


    def send_request(self, message):
        '''
        Sends the given message.

        :param dict message: The message to send.            
        '''
        json_string = json.dumps(message, cls=MyEncoder)
        jsonrpc_req = self.__add_header(json_string)
        with self.write_lock:
            # self.stdin.write(jsonrpc_req.encode())
            # self.stdin.flush()
            self.stdin.send(jsonrpc_req.encode())


    def recv_response(self):
        '''        
        Recives a message.

        :return: a message
        '''
        with self.read_lock:
            message_size = None
            while True:
                #read header
                # line = self.stdout.readline()
                buf = io.BytesIO()
                c = ''
                while c != b'\n':
                    c = self.stdout.recv(1)
                    buf.write(c)
                line = buf.getvalue()
                if not line:
                    # server quit
                    return None
                line = line.decode("utf-8")
                if not line.endswith("\r\n"):
                    raise RuntimeError("Bad header: missing newline")
                #remove the "\r\n"
                line = line[:-2]
                if line == "":
                    # done with the headers
                    break
                elif line.startswith(LEN_HEADER):
                    line = line[len(LEN_HEADER):]
                    if not line.isdigit():
                        raise RuntimeError("Bad header: size is not int")
                    message_size = int(line)
                elif line.startswith(TYPE_HEADER):
                    # nothing todo with type for now.
                    pass
                else:
                    raise RuntimeError("Bad header: unkown header")
            if not message_size:
                raise RuntimeError("Bad header: missing size")

            # jsonrpc_res = self.stdout.read(message_size).decode("utf-8")
            jsonrpc_res = self.stdout.recv(message_size).decode("utf-8")
            return json.loads(jsonrpc_res)

if __name__ == '__main__':
    import socket

    id = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 7920))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client = JsonRpcEndpoint(s, s)

        def initialize(client):
            global id
            id += 1
            client.send_request({"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": id})
            return client.recv_response()
        def show(client):
            global id
            id += 1
            client.send_request({"jsonrpc": "2.0", "method": "show", "params": {}, "id": id})
            return client.recv_response()
        def hide(client):
            global id
            id += 1
            client.send_request({"jsonrpc": "2.0", "method": "hide", "params": {}, "id": id})
            return client.recv_response()
        def render_text(client, filepath):
            global id
            id += 1
            with open(filepath) as f:
                content = ''.join(f.readlines())
            client.send_request({"jsonrpc": "2.0", "method": "render_text", "params": {"textDocument": {'uri': filepath, 'content': content}}, "id": id})
            return client.recv_response()
        from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

