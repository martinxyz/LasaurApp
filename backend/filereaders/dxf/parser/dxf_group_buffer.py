
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import StringIO
import logging

from filereaders.dxf.dxf_value import DXFValue


log = logging.getLogger(__name__)

class DXFGroupBuffer:

    def __init__(self, buf):
        self.stringio = StringIO.StringIO(buf)

    def __iter__(self):
        return self

    def next(self):
        """

        :return: a group code and the according value
        :rtype: :func:`list`
        :raises StopIteration: if the iterator is at the end of the buffer
        :raises ValueError: if the buffer ends abruptly/unexpected
        """
        groupCode = self.stringio.readline()
        if not groupCode:
            raise StopIteration
        try:
            groupCode = int(groupCode.strip())
        except ValueError:
            pass

        value = self.stringio.readline()
        if not value:
            raise ValueError('Premature end of file!')
        value = DXFValue(value.strip())

        log.debug("%-3i : %s", groupCode, value)
        return groupCode, value
