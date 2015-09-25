from common import config
from common import util

class entityObject(object):
    """Read YAML config file to get access info
      (device ip, tcp port, user name, keys, etc)
    """
    def __init__(self, entities_yml_file=config.cfg.entities_yml_file, *args, **kwargs):
        self.entities_yml_file = entities_yml_file
        self.entities = util.read_data_file(self.entities_yml_file)
        self.users = util.myDict(self.getUsers())
        self.devices = util.myDict(self.getDevices())

    def getUsers(self):
        return self.entities.snmpv3_users


    def getDevices(self):
        return self.entities.devices

entities = entityObject()
