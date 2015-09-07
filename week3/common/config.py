from ConfigParser import ConfigParser
from common import util

class configObject(object):
    """Read YAML config file to get config info
      (file names etc)
    """
    def __init__(self, config_file="etc/default.conf", *args, **kwargs):
        self.config_file = config_file
        self.cfg = ConfigParser()
        self.cfg.read(self.config_file)
    
        self.entities_yml_file = self.cfg.get('Files', 'entities_yml_file')
        self.oids_yml_file = self.cfg.get('Files', 'oids_yml_file')
        self.data_file_folder = self.cfg.get('Files', 'data_file_folder')


cfg = configObject()
