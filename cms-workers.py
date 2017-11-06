#!/usr/bin/env python

## For Python2
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
## For Python3
from http.server import BaseHTTPRequestHandler, HTTPServer

import time, time
import base64, json
import subprocess, sys, random

assert(len(sys.argv) == 2)
config = json.load(open(sys.argv[1], 'r'))

from job import Job
from jobs import Jobs

queues = Jobs(config)

class Handler(BaseHTTPRequestHandler):
    def build_job(self):
        j = Job(config)
        content_length = int(self.headers['Content-Length'])
        j.set(self.rfile.read(content_length))
        return queues.add(j)

    def do_POST(self):
        jid = self.build_job()
        queues.update()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes(jid, 'utf8'))

    def do_GET(self):
        queues.update()

        if self.path == "/" or self.path == "/jobs" or self.path == "/jobs/":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(queues.overview(), 'utf8'))
            return

        if self.path == "/update" or self.path == "/update/":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes("updated", 'utf8'))
            return

        if len(self.path) > 5 and self.path[0:5] == "/job/":
            jid = self.path[5:]
            j = queues.get(jid)

            if not j:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes("Job not found: " + jid, 'utf8'))
                return

            if j.status():
                # Job has finished
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(queues.result(j), 'utf8'))
                return

            self.send_response(202)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(queues.status(j), 'utf8'))
            return

        if len(self.path) > 6 and self.path[0:6] == "/kill/":
            jid = self.path[6:]
            j = queues.get(jid)

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
            j = queues.get(jid)

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

print("Config:")
print(config)
httpd = HTTPServer((config["hostname"], config["port"]), Handler)
httpd.serve_forever()
