import requests

class Weave:
    def add_server(self, hostname, port):
        assert(type(hostname) == str)
        assert(type(port) == int)
        ns = "http://" + hostname + ":" + str(port)
        self.known_servers.add(ns)

    def check_servers(self):
        for server in self.known_servers:
            self.check_server(server)

    def check_server(self, server):
        assert(server in known_servers)
        r = request.get(server + "/status")
        if r.status_code == 200:
            if r.text == "true":
                self.ready_servers.add(server)
            else:
                self.ready_servers.remove(server)
