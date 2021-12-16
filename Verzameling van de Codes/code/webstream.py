from os import read
import logging
import socketserver
from http import server
import cv2 as cv
import numpy as np
from threading import Thread
from time import time, sleep


class StreamingHandler(server.BaseHTTPRequestHandler):
    buffer = None
    def do_GET(self):

        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

        elif self.path == '/index.html':
            content = read_file('templates/index.html')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/main.js' or self.path == '/panolens.min.js' or self.path == '/three.min.js':
            content = read_file(f'static{self.path}')
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/style.css':
            content = read_file('static/style.css')
            self.send_response(200)
            self.send_header('Content-Type', 'text/css')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    # with output.condition:
                    #     output.condition.wait()
                    #     frame = output.frame
                    _, image = StreamingHandler.buffer.get()
                    _, frame = cv.imencode('.jpg', image)

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))

        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def read_file(path):
    with open(path, 'r') as f:
        return f.read().encode('utf-8')


def start_server(address, buffer):
    StreamingHandler.buffer = buffer
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
