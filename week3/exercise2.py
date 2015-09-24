from common import config
from common.entities import entities
from common import oids
from common.util import send_email
from common.util import get_snmp_data
from pygal import Line
from random import randint
from time import sleep

class snmpDataMetric(object):
    def __init__(self, dev_name, metric, snmp_index):
        self.dev_name = dev_name
        self.metric = metric
        self.snmp_index = snmp_index
        self.reset_values()

    def reset_values(self):
        self.values = {}
    
    def set_value(self, data_point, value):
        self.values.update({data_point: value})
    
    def get_values(self):
        return self.values

    def get_value_by_data_point(self, data_point):
        return self.values.get('data_point', 'NaN')

    def compute_values(self):
        values = self.get_values()
        data_points = values.keys()
        data_points.sort()
        previous_value = 0
        computed_values = []
        for data_point in data_points:
            current_value = values.get(data_point)
            if previous_value == 0:
                computed_value = 0
            else:
                computed_value = current_value - previous_value
            previous_value = current_value
            

    def __repr__(self):
        return "<snmpDataMetric(%s, %s, %s)>" % (
            self.dev_name,
            self.metric,
            self.snmp_index,
        )
         
        
class graphInterfaces(object):

    def __init__(self, **kwargs):
        self.last = 555559
        self.test = True
        self.devices = entities.devices
        self.user_tuple = entities.users.user1
        self.oid_groups = kwargs.get('oid_groups',
            {
                'Unicast Packets':
                    ('ifInUcastPkts', 'ifOutUcastPkts'),
                'Octets':
                    ('ifInOctets', 'ifOutOctets'),
            }
        )
        self.device_dict = kwargs.get(
            'devices_dict',
            {'rtr1': [5]}
        )
        self.init_metrics()
        self.oids_dict = self.my_oids()
        self.start = kwargs.get(
            'start',
            int(config.cfg.cfg.get('Line Graphs', 'start'))
        )
        self.step = kwargs.get(
            'step',
            int(config.cfg.cfg.get('Line Graphs', 'step'))
        )
        self.stop = kwargs.get(
            'stop',
            int(config.cfg.cfg.get('Line Graphs', 'stop'))
        )
        self.units = kwargs.get(
            'units',
            config.cfg.cfg.get(
                'Line Graphs',
                'units'
        ))
        self.points = range(self.start, self.stop + 1, self.step)

    def _oids_in_groups(self):
        oids_in_groups = []
        for group_name, oids in self.oid_groups.iteritems():
            oids_in_groups.extend(oids)
        return oids_in_groups
            
    def init_metrics(self):
        self.metrics = []
        oid_descs = self._oids_in_groups()    
        for oid_desc in oid_descs:
            for dev_name, snmp_indexes in self.device_dict.iteritems():
                for snmp_index in snmp_indexes:
                    self.metrics.append(snmpDataMetric(dev_name, oid_desc, snmp_index))
        print self.metrics

    def my_oids(self):
        oids_dict = {}
        oids_desc = [
            'ifAlias',
            'ifDescr',
        ]
        oids_desc.extend(self._oids_in_groups())
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
        if self.test is True:
            self.last = self.last + randint(100, 2000)
            snmp_data = self.last
            return snmp_data
        oid_string = '.'.join([oid_string, str(index)])
        print "DEBUG: oid_string:", oid_string
        snmp_data = get_snmp_data(
            tuple(device_tuple),
            tuple(self.user_tuple),
            oid_string
        )
        return snmp_data

    def devices_indexes(self):
        for dev_name, snmp_indexes in self.device_dict.iteritems():
            device_tuple = self.devices.get(dev_name)
            for snmp_index in snmp_indexes:
                yield dev_name, snmp_index

    def poll_oids(self, device_tuple, snmp_index):
        data = {}
        for oid_name in self._oids_in_groups():
            print "DEBUG: oid_name:", oid_name
            oid_string = self.oids_dict.get(oid_name)
            print "DEBUG: oid_string:", oid_string
            print "DEBUG: snmp_index:", snmp_index
            data[oid_name] = self.get_snmp(
                device_tuple,
                oid_string,
                snmp_index
            )
        return data

    def get_data_stream(self, dev_name, metric, snmp_index):
        for data_stream in self.metrics:
            if (
                data_stream.dev_name,
                data_stream.metric,
                data_stream.snmp_index
            ) == (dev_name, metric, snmp_index):
                return data_stream
        return None

    def run(self):
        for point in self.points:
            devices_indexes = self.devices_indexes()
            for dev_name, snmp_index in devices_indexes:
                device_tuple = self.devices.get(dev_name)
                data = self.poll_oids(device_tuple, snmp_index)
                for metric, value in data.iteritems():
                    data_stream = self.get_data_stream(
                        dev_name,
                        metric,
                        snmp_index
                    )
                    data_stream.set_value(point, value)
            for metric in self.metrics:
                print metric, metric.get_values()
            sleep(int(self.step) * 1)


def test():
    return graphInterfaces()