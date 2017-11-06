import base64, random
import requests, subprocess

class Client:
    def __init__(self, max_jobs=0, config=None):
        self.all_jobs = set()
        self.submitted = set()
        self.finished = set()
        self.max_jobs = max_jobs
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
    def __init__(self, max_jobs=0, config=None):
        self.jobs = {}
        super().__init__(max_jobs=max_jobs, config=config)

    def ready():
        return self.submitted < self.max_jobs

    def add_sat(self, cnf):
        jid = self._ri()

        f_out = open(self.cms['sats'])

        cmd = [self.config['cms']]
        cmd += self.config["cms_args"].split(" ")
        cmd.append(cnf)

        output = open()


        self.all_jobs.add(r.text)
        self.submitted.add(r.text)
        return jid

    def _ri(self):
        return str(random.randint(10000000, 99999999))


class RemoteClient(Client):
    def __init__(self, max_jobs=0, config=None, uri=None):
        assert(uri != None)
        self.uri = uri
        super().__init__(max_jobs=max_jobs, config=config)
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

        self.all_jobs.add(r.text)
        self.submitted.add(r.text)

        return True
