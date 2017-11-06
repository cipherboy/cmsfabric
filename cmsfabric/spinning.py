import subprocess

class Spinning:
    def __init__(self):
        self.worker_servers = set()
        self.port_forwards = set()
        self.servers = {}
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

    def setup_server_ssh(self, hostname):
        cmds = ["wget https://cipherboy.com/cmsfabric.tar.gz", "tar -xf cmsfabric.tar.gz"]
        for cmd in cmds:
            r = self.run_ssh(host, cmd)
            if r == None or r != 0:
                print("Failed command: " + cmd)
                print(r)

    def add_server_ssh(self, hostname, config):
        n_p = subprocess.Popen(["ssh", hostname, "python cmsfabric/workers.py .cmsfabric.conf"])

    def add_server_uri(self, host, port, config):
