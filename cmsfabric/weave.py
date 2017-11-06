from cmsfabric.spinning import *

class Weave:
    def __init__(self):
        self.spinning = Spinning()

    def spin_from_object(self, config):
        for server_config in config:
            if server_config['type'] == 'ssh':
                self.spinning.add_server_ssh(server_config["ssh_host"], server_config)
            if server_config['type'] == 'uri':
                self.spinning.add_server_ssh(server_config["uri_host"], server_config["uri_port"], server_config)
            if server_config['type'] == 'local':
                self.spinning.add_local(server_config)
