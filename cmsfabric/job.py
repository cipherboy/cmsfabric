import time, os, shutil
import base64, json
import subprocess, sys, random

from cmsfabric.utils import *

class Job:
    def __init__(self, config):
        # Copy config
        self.config = config.copy()
        self.id = u_ri()

        self.cms = u_p([self.config["home"], self.config["cms"]])
        self.cfname = u_p([self.config["home"], self.config["sats"],
                               "test-" + self.id + ".cnf"])
        self.ofname = u_p([self.config["home"], self.config["sats"],
                               "test-" + self.id + ".out"])
        self.of = open(self.ofname, 'w')
        self.p = None
        self.stime = 0
        self.rtime = 0
        self.ftime = 0

    def set(self, post_data):
        f = open(self.cfname, 'w')
        f.write(str(base64.b64decode(post_data), 'utf8'))
        f.flush()
        f.close()
        self.stime = time.time()

    def load(self, cnf_path):
        shutil.copyfile(cnf_path, self.cfname)
        self.stime = time.time()

    def run(self):
        cmd = [self.cms]
        if self.config["cms_args"] != '':
            cmd += self.config["cms_args"].split(" ")
        cmd.append(self.cfname)

        self._p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=self.of)
        self.rtime = time.time()

    def status(self):
        if self._p.poll() != None:
            if not self.of.closed:
                self.of.flush()
                self.of.close()
            self.ftime = time.time()
            return self._p.returncode
        return None

    def kill(self):
        if self._p.poll() == None:
            self._p.kill()
            self._p.terminate()
        self.ftime = time.time()

    def get(self):
        f = open(self.ofname, 'r')
        b = base64.b64encode(bytes(f.read(), 'utf8'))
        s = str(b, 'utf8')
        f.close()
        return {"id": self.id, "return": self.status(), "out": s}

    def result(self):
        return {"id": self.id, "return": self.status(), "out": self.ofname}

    def clean(self):
        try:
            os.remove(self.cfname)
            os.remove(self.ofname)
        except:
            pass
