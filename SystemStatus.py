from collections import namedtuple


class SystemStatus:
    _Status = namedtuple('_Status', ['freq', 'timeout'])
    Idle = _Status(0.5, None)
    Playing = _Status(2, 1)
