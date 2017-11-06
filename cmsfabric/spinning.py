import base64, json
import subprocess, random, time
from cmsfabric.clients import *

class Spinning:
    def __init__(self):
        self.worker_servers = {}
        self.port_forwards = {}
        self.configs = {}
        self.servers = set()
        self.running_jobs = {}
        self.finished_jobs = {}
        self.results = {}
        self.clients = {}
        pass

    def run_ssh(self, host, command, timeout=None):
        try:
            n_p = subprocess.Popen(["ssh", host, command], stdin=subprocess.DEVNULL)
            n_p.wait(timeout)
        except:
            if n_p and n_p.poll() is None:
                n_p.kill()
                n_p.terminate()
            raise
        if n_p:
            return n_p.poll()
        return None

    def setup_server_ssh(self, host):
        cmds = ["wget https://cipherboy.com/cmsfabric.tar.gz", "tar -xf cmsfabric.tar.gz"]
        for cmd in cmds:
            r = self.run_ssh(host, cmd)
            if r == None or r != 0:
                print("Failed command: " + cmd)
                print(r)

    def add_server_ssh(self, hostname, config):
        n_p = subprocess.Popen(["ssh", hostname, "base64 -d > .cmsfabric.conf"])
        base64_config = str(base64.b64encode(bytes(json.dumps(config), 'utf8')), 'utf8')
        n_p.communicate(base64_config)

        n_p = subprocess.Popen(["ssh", hostname, "python cmsfabric/workers.py .cmsfabric.conf"])
        self.worker_servers[hostname] = n_p

        n_p = subprocess.Popen(["ssh" "-L", str(config["socks_port"]) + ":" + config["hostname"] + ":" + str(config["port"]), "-n", hostname])
        self.port_forwards[hostname] = n_p

        self.servers.add(hostname)
        self.configs[hostname] = config
        self.clients[hostname] = RemoteClient(config, "localhost:" + str(config["socks_port"]))
        self.running_jobs[hostname] = set()
        self.finished_jobs[hostname] = set()

    def add_server_uri(self, host, port, config):
        hostname = host + ":" + str(port)
        self.servers.add(hostname)
        self.configs[hostname] = config
        self.clients[hostname] = RemoteClient(config, hostname)
        self.running_jobs[hostname] = set()
        self.finished_jobs[hostname] = set()

    def add_local(self, config):
        self.servers.add("local")
        self.configs["local"] = config
        self.clients["local"] = LocalClient(config)
        self.running_jobs["local"] = set()
        self.finished_jobs["local"] = set()

    def server_list(self):
        sl = list(self.servers)
        random.shuffle(sl)
        return sl

    def running_job_list(self, server):
        jl = list(self.running_jobs[server])
        random.shuffle(jl)
        return jl

    def all_ready_clients(self):
        result = set()
        for client in self.servers:
            if self.clients[client].ready():
                results.add(client)
        return result

    def any_ready_client(self):
        for client in self.server_list():
            if self.clients[client].ready():
                return client
        return None

    def add_sat(self, cnf):
        client = None
        delay = 0
        while client == None:
            time.sleep(delay)
            client = any_ready_client()
            if client == None and delay < 10:
                delay += 0.1
        jid = self.clients[client].add_sat(cnf)
        self.running_[client].add(jid)
        return jid

    def update_finished_jobs(self):
        newly_finished = {}
        for client in self.servers:
            for j in self.running_jobs[client]:
                if self.clients[client].finished(j):
                    newly_finished[j] = client
                    self.running_jobs[client].remove(j)
                    self.finished_jobs[client].add(j)
        return newly_finished

    def fetch_finished(self, finished):
        for j in finished:
            c = finished[j]
            self.results[j] = self.clients[c].result(j)

    def have_remaining_jobs(self):
        self.update_finished_jobs()
        for client in self.servers:
            if len(self.running_jobs[client]) > 0:
                return True
        return False
