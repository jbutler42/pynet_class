from common import util

class configObject(object):
    """Read YAML config file to get config info
      (file names etc)
    """
    def __init__(self, config_file="etc/default.conf", *args, **kwargs):
        self.config_file = config_file
        self.cfg = util.load_yaml_from_file(self.config_file)
    
        self.entities_yml_file = self.cfg.get('entities_yml_file')
        self.oids_yml_file = self.cfg.get('oids_yml_file')


cfg = configObject()
