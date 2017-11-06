import base64, json
import requests, subprocess

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
        self.all_jobs = self.queue.fj + self.queue.jq + self.queue.wj
        self.submitted = self.queue.jq + self.queue.wj
        self.finished = self.queue.fj

    def add_sat(self, cnf):
        j = Job(self.config)
        j.load(cnf)
        self.queue.add(j)
        self.update()

    def finished(self, id):
        j = self.queue.get(id)
        if j == None:
            return None
        return j.status() != None

    def result(self, id):
        j = self.queue.get(id)
        if j == None or not self.finished(j):
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
        print(self.all_jobs)

    def ready(self):
        r = requests.post(self.uri + "/ready")
        if r.status_code == 200:
            return bool(r.text)
        return False

    def add_sat(self, cnf):
        cnf_file = open(cnf, 'r')
        cnf = cnf_file.read().encode('utf8')
        base64_cnf = base64.b64encode(cnf)

        r = requests.post(self.uri + "/jobs", data=base64_cnf.encode('utf8'))
        if r.status_code != 200:
            return False
        if int("0" + r.text) == 0:
            return False

        self.update()

        return True

    def update(self):
        r = requests.get(self.uri + "/jobs")
        if r.status_code != 200:
            return
        d = json.dumps(r.text)
        self.fj = set(d['fj'])
        self.jq = set(d['jq'])
        self.wj = set(d['wj'])

    def finished(self, id):
        r = requests.get(self.uri + "/state/" + id)
        if r.status_code == 404:
            return None
        elif r.status_code == 200:
            return True

        return False

    def result(self, id):
        j = self.queue.get(id)
        if j == None or not self.finished(j):
            return None

        r = requests.get(self.uri + "/job/" + id)
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            return None

        d = r.json()
        out_text = str(base64.b64decode(bytes(d['out'], 'utf8')), 'utf8')
        out_file = config['out_path'] + "/" + d['id'] + ".out"
        of = open(out_file, 'w')
        of.write(out_text)
        of.flush()
        of.close()
        d['out'] = out_file
        return d
