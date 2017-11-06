from multiprocessing import Pool

from cmsfabric.spinning import *

class Weave:
    def __init__(self):
        self.spinning = Spinning()
        self.loom = None
        self.data = {}

    def spin_from_object(self, config):
        for server_config in config:
            if server_config['type'] == 'ssh':
                self.spinning.add_server_ssh(server_config["ssh_host"], server_config)
            if server_config['type'] == 'uri':
                self.spinning.add_server_ssh(server_config["uri_host"], server_config["uri_port"], server_config)
            if server_config['type'] == 'local':
                self.spinning.add_local(server_config)

    def set_loom(self, loom):
        self.loom = loom
        self.loom.set_weave(self)

    def run(self):
        pool = Pool(processes=4)

        self.loom.start()

        work = self.loom.gen_work()
        cnfs = pool.map(self.loom.pre_run, work)

        for i in range(len(work)):
            jid = self.spinning.add_sat(cnfs[i])
            self.data[jid] = (jid, cnfs[i], work[i])

        while self.spinning.have_remaining_jobs():
            newly_finished = self.spinning.fetch_finished()
            for jid in newly_finished:
                self.loom.post_run(self.spinning.results[jid], self.data[jid])

        self.loom.stop()
