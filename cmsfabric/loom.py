# Base Class

class Loom:
    def __init__(self):
        self.weave = None
        self.quit = False
        pass

    def set_weave(self, weave):
        self.weave = weave

    def post_run(self, obj, data):
        if obj["return"] == 10:
            return self.run_sat(obj["out"], data, raw=obj)
        elif obj["return"] == 20:
            return self.run_unsat(obj["out"], data, raw=obj)
        else:
            return self.run_error(obj["out"], data, raw=obj)

    def start(self):
        pass

    def gen_work(self):
        return []

    def pre_run(data):
        pass

    def run_sat(self, path, data, raw=None):
        pass

    def run_unsat(self, path, data, raw=None):
        pass

    def run_error(self, path, data, raw=None):
        print("[Error]")
        print(raw)

    def stop(self):
        pass

    def quit(self):
        self.quit = True
