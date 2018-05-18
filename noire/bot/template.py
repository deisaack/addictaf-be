def login(self, **args):
    if self.proxy:
        args['proxy'] = self.proxy
    if super(Bot, self).login(**args) is False:
        return False
    self.prepare()
    signal.signal(signal.SIGTERM, self.logout)
    atexit.register(self.logout)
    return True
