from pdu import decodeSmsPdu, encodeSmsSubmitPdu, Concatenation
import abc
from datetime import datetime
import redis

try:
    r = redis.Redis("localhost", 6379,db=0)
    print("Redis Clinet Connect .......")    

except Exception as e:      
    print(e)

class Sms(object):
    """ Abstract SMS message base class """
    __metaclass__ = abc.ABCMeta

    # Some constants to ease handling SMS statuses
    STATUS_RECEIVED_UNREAD = 0
    STATUS_RECEIVED_READ = 1
    STATUS_STORED_UNSENT = 2
    STATUS_STORED_SENT = 3
    STATUS_ALL = 4
    # ...and a handy converter for text mode statuses
    TEXT_MODE_STATUS_MAP = {'REC UNREAD': STATUS_RECEIVED_UNREAD,
                            'REC READ': STATUS_RECEIVED_READ,
                            'STO UNSENT': STATUS_STORED_UNSENT,
                            'STO SENT': STATUS_STORED_SENT,
                            'ALL': STATUS_ALL}

    def __init__(self, number, text, smsc=None):
        self.number = number
        self.text = text
        self.smsc = smsc

class ReceivedSms(Sms):
    """ An SMS message that has been received (MT) """

    def __init__(self, status, number, time, text, smsc=None, udh=[]):
        super(ReceivedSms, self).__init__(number, text, smsc)
        self.status = status
        self.time = time
        self.udh = udh



def handleSms(sms):
    concat = None
    message = None
    for i in sms.udh:
        if isinstance(i, Concatenation):
            concat = i
            break
    if concat:
        # if (concat.reference in concat_sms) == False:
        if (r.hexists(concat.reference,"")) == False:
            # r.hmset(concat.reference,{None:None})
            r.hset(concat.reference,concat.number,sms.text)
            # concat_sms[concat.reference] = {} #numpy.empty(concat.parts, dtype=string)
        # concat_sms[concat.reference][concat.number] = sms.text
        r.hset(concat.reference,concat.number,sms.text)
        #print(u'== Partial message received ==\n[{0}/{1}] reference{2}\n'.format(len(concat_sms[concat.reference]), concat.parts, concat.reference))
        
        if r.hlen(concat.reference) == concat.parts:
            d = r.hgetall(concat.reference)
            x = { y.decode(): d.get(y).decode() for y in d.keys() }
            sortedParts = sorted(x.items())
            message = "".join([x[1] for x in sortedParts])
            r.delete(concat.reference)
    else:
        message = sms.text

    if message:
        return sms.number, sms.time, message
    else:
        return None
 