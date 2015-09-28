class ciscoDriver(object):
    def __init__(self, os):
        self.os = self.getOS(os)
        self.tasklist = self.getTaskList()

    def taskList(self, *args):
        tasklist = {
            'disable paging': {
                'modes': ['top'],
            },
            'log buffer size': 1,
        }
        if args:
            t_list = [tasklist.get(a) for a in args]
        else:
            t_list = tasklist
        return t_list

    def getOS(self, os):
        os = os.lower()
        supported_os = [
            'ios',
            'nxos',
            'iosxr',
            'catos',
        ]
        if supported_os.count(os):
            return os
        else:
            raise "Unspported OS:", os
