try:
    # For Python2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except:
    # For Python3
    from http.server import BaseHTTPRequestHandler, HTTPServer

import time, time
import base64, json
import subprocess, sys, random

from cmsfabric.job import Job
from cmsfabric.jobs import Jobs

class Handler(BaseHTTPRequestHandler):
    config = None
    queues = None

    def build_job(self):
        j = Job(Handler.config)
        content_length = int(self.headers['Content-Length'])
        j.set(self.rfile.read(content_length))
        return Handler.queues.add(j)

    def do_POST(self):
        jid = self.build_job()
        Handler.queues.update()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes(jid, 'utf8'))

    def do_GET(self):
        Handler.queues.update()

        if (self.path == "/" or self.path == "/status" or
            self.path == "/status/"):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(Handler.queues.overview(), 'utf8'))
            return

        if self.path == "/update" or self.path == "/update/":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("updated", 'utf8'))
            return

        if self.path == "/ready" or self.path == "/ready/":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(Handler.queues.ready()), 'utf8')
            return

        if self.path == "/jobs" or self.path == "/jobs/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(Handler.queues.all(), 'utf8'))
            return

        if len(self.path) > 7 and self.path[0:7] == "/state/":
            jid = self.path[7:]
            j = Handler.queues.get(jid)

            if not j:
                # Job not found
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                return

            if j.status():
                # Job has finished
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                return

            # Job hasn't finished
            self.send_response(202)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            return



        if len(self.path) > 5 and self.path[0:5] == "/job/":
            jid = self.path[5:]
            j = Handler.queues.get(jid)

            if not j:
                # Job not found
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes("Job not found: " + jid, 'utf8'))
                return

            if j.status():
                # Job has finished
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(Handler.queues.result(j), 'utf8'))
                return

            # Job hasn't finished
            self.send_response(202)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(Handler.queues.status(j), 'utf8'))
            return

        if len(self.path) > 6 and self.path[0:6] == "/kill/":
            jid = self.path[6:]
            j = Handler.queues.get(jid)

            if not j:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes("Job not found: " + jid, 'utf8'))
                return

            j.kill()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            return

        if len(self.path) > 5 and self.path[0:5] == "/del/":
            jid = self.path[5:]
            j = Handler.queues.get(jid)

            if not j:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes("Job not found: " + jid, 'utf8'))
                return

            j.clean()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            return

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

class Worker:
    def run(config):
        Handler.config = config
        Handler.queues = Jobs(Handler.config)

        httpd = HTTPServer((Handler.config["hostname"], Handler.config["port"]), Handler)
        httpd.serve_forever()

    def __main__():
        assert(len(sys.argv) == 2)

        config = json.load(open(sys.argv[1], 'r'))
        Worker.run(config)


if __name__ == "__main__":
    Worker.__main__()
