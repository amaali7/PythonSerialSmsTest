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
        print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, message))
        
 
fresult = ["0891421952804714F3440C914219125432650008023070610352808C050003840301062C06330642064606410020064606410646062F063300200633002006340020063306410633063006330020064706410633062F063300300633062F063306300633064106330020062F0633062F0633062C06330641063300200633064106330630002006300627063306270633064100200633062F0633062C0633062F00200633062F0633","0891421952804714F3400C914219125432650008023070610382808C050003840302062C06300633002006300633062C002E06280020062F0633062C06330628062F0020062F0633062D0633062F0020062F0633062D062F0020063306300633062C062F06330020062F0633062D0633002E0020062F0633062C0633062F06330020062F0633062C0633062F06280633062C0641002006410646062D0633062F06330628002E0020","0891421952804714F3440C9142191254326500080230706103038022050003840303062F0633062C0633062F0633062806330020062F0633062C0633062F"]

messages = []
for sms in fresult:

    smsDict = decodeSmsPdu(sms)
    nsms = ReceivedSms( 0, smsDict['number'], smsDict['time'], smsDict['text'], smsDict['smsc'], smsDict.get('udh', []))
    messages.append(nsms)

index = 1
for massage in messages:
    handleSms(massage)

