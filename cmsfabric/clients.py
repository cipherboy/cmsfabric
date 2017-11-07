import base64, json
import requests, subprocess

from cmsfabric.jobs import *
from cmsfabric.utils import *

class Client:
    def __init__(self, config=None):
        self.config = config

    def ready(self):
        return True

    def add_sat(self, cnf):
        pass

    def finished(self, id):
        return False

    def result(self, id):
        pass

class LocalClient(Client):
    def __init__(self, config=None):
        self.queue = Jobs(config)
        super().__init__(config=config)

    def ready():
        return self.queue.ready()

    def update(self):
        self.queue.update()

    def add_sat(self, cnf):
        j = Job(self.config)
        j.load(cnf)
        self.queue.add(j)
        self.update()
        return j.id

    def finished(self, id):
        j = self.queue.get(id)
        if j == None:
            return None
        return j.status() != None

    def result(self, id):
        j = self.queue.get(id)
        if j == None or not self.finished(id):
            return None
        return j.result()

class RemoteClient(Client):
    def __init__(self, config=None, uri=None):
        assert(uri != None)
        self.uri = uri
        self.fj = set()
        self.jq = set()
        self.wj = set()
        super().__init__(config=config)

    def ready(self):
        r = requests.get(self.uri + "/ready/")
        if r.status_code == 200:
            return bool(r.text)
        return False

    def add_sat(self, cnf):
        cnf_file = open(cnf, 'r')
        cnf = cnf_file.read().encode('utf8')
        base64_cnf = base64.b64encode(cnf)

        r = requests.post(self.uri + "/jobs/", data=base64_cnf)
        if r.status_code != 200:
            return False
        if int("0" + r.text) == 0:
            return False

        jid = r.text
        self.update()

        return jid

    def update(self):
        r = requests.get(self.uri + "/update/")
        if r.status_code != 200:
            return
        d = json.loads(r.text)
        self.fj = set(d['fj'])
        self.jq = set(d['jq'])
        self.wj = set(d['wj'])

    def finished(self, id):
        r = requests.get(self.uri + "/status/" + id)
        if r.status_code == 404:
            return None
        elif r.status_code == 200:
            return True

        return False

    def result(self, id):
        print("Fetching result: " + id)
        if not self.finished(id):
            print("Result not finished")
            return None

        r = requests.get(self.uri + "/job/" + id)
        print("Fetched: " + str(r.status_code))
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            return None

        d = r.json()
        out_text = str(base64.b64decode(bytes(d['out'], 'utf8')), 'utf8')
        out_file = self.config['out_path'] + "/" + d['id'] + ".out"
        of = open(out_file, 'w')
        of.write(out_text)
        of.flush()
        of.close()
        d['out'] = out_file
        return d
