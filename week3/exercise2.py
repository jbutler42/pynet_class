from pygal import Line
from common import config
from common.entities import entities
from common import oids
from common.util import send_email
from common.util import get_snmp_data

class graphInterfaces(object):

    def __init__(self, **kwargs):
        self.devices = entities.devices
        self.user_tuple = entities.users.user1
        self.oids_dict = self.my_oids()
        self.device_dict = kwargs.get('devices_dict', {'rtr1': [5]})
        self.start = kwargs.get('start', config.cfg.cfg.get('Line Graphs', 'start'))
        self.step = kwargs.get('step', config.cfg.cfg.get('Line Graphs', 'step'))
        self.stop = kwargs.get('stop', config.cfg.cfg.get('Line Graphs', 'stop'))
        self.units = kwargs.get('units', config.cfg.cfg.get(
            'Line Graphs',
            'units'
        ))
        self.points = range(self.start, self.stop + 1, self.step)
        self.values_dict = self.init_values()
      
    
    def init_values(self):
        values = {}
        for dev_name, indexes in self.device_dict.iteritems():
            for oid in self.oids_dict.iterkeys():
                values.update(
                    {
                        dev_name: {
                            oid: {
                                'points': {},
                            },
                        },
                    },
                )
                for point in self.points:
                    for index in indexes:
                        values[dev_name][oid]['points'].update(
                            {
                                point: {
                                    index: 0
                                }
                            }
                        )
        return values


    @staticmethod 
    def my_oids():
        oids_dict = {}
        oids_desc = [
            'ifAlias',
            'ifDescr',
            'ifInUcastPkts',
            'ifOutUcastPkts',
            'ifInOctets',
            'ifOutOctets',
        ]
        for oid in oids_desc:
            oids_dict.update({oid: oids.get(oid)})
        return oids_dict
    
    def get_line_chart(self, title, lines):
        """Make chart of type line and return it.
        
        title: Title of chart (string)
        step: x label step and poll interval (integer)
        start: x label start value (integer)
        stop: x label end value and end of polling (integer)
        lines: tuple or list of tuples or lists (line_name, data_points)
            line_name (string)
            data_points (list of ints)
    
        returns line_chart (pygal.Line())
        """
    
        chart = Line()
        chart.title = title
        chart.x_labels = self.points
        if type(lines[0]) == type(str()):
            lines = list(lines)
        for line in lines:
            label = line[0]
            data = line[1]
            chart.add(label, data)
        return chart
   
    @staticmethod 
    def save_chart(file_name, chart):
        try:
            chart.render_to_file(file_name)
        except Exception as e:
            print "ERROR: Could not render chart data to file: ", e
            return False
        return True

    def get_snmp(self, device_tuple, oid_string, index):
        oid_string = oid_string + index
        snmp_data = get_snmp_data(
            tuple(device_tuple),
            tuple(self.user_tuple),
            oid_string
        )
        return snmp_data

    def walk_snmp_oid(self, device_tuple, oid_string):
        # there is no 'walk' in the snmp_helper
        pass

    def get_ifdescr(self):
        oid_string = self.oids_dict.get('ifDescr')
        for dev_name, indexes in self.devices_dict.iteritems():
            device_tuple = self.devices.get(dev_name)
            for index in indexes:
                print dev_name, self.get_snmp(device_tuple, oid_string, index)

    def get_next_values(self, oids_list=None):
        if oids_list is None:
            oids_list = [
                'ifInUcastPkts',
                'ifOutUcastPkts',
                'ifInOctets',
                'ifOutOctets',
            ]
        oid_strings = [self.oids_dict.get(o) for o in [oids_list]]
        for dev_name, indexes in self.devices_dict.iteritems():
            device_tuple = self.devices.get(dev_name)
            for index in indexes:
                for oid in oids_list:
                    oid_string = self.oids_dict.get(oid_string)
                    data = get_snmp(device_tuple, oid_string, index)
                    values[dev_name][oid][
