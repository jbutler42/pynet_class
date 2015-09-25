from ConfigParser import ConfigParser
from pyclass.common import util

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
        self.reload_max_last_changed = float(self.cfg.get('Device Settings', 'reload_max_last_changed'))
        self.loop_pause_seconds = float(self.cfg.get('Runtime Options', 'loop_pause_seconds'))
        self.email = {
            'email_enabled': self.cfg.getboolean('Email', 'email_enabled'),
            'email_from': self.cfg.get('Email', 'from'),
            'email_to': self.cfg.get('Email', 'to'),
        }


cfg = configObject()
