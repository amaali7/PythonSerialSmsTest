from pdu import decodeSmsPdu, encodeSmsSubmitPdu, Concatenation
import abc
from datetime import datetime


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


concat_sms = {}
def handleSms(sms):
    concat = None
    message = None
    for i in sms.udh:
        if isinstance(i, Concatenation):
            concat = i
            break
    if concat:
        if (concat.reference in concat_sms) == False:
            concat_sms[concat.reference] = {} #numpy.empty(concat.parts, dtype=string)
        concat_sms[concat.reference][concat.number] = sms.text
        print(u'== Partial message received ==\n[{0}/{1}] reference{2}\n'.format(len(concat_sms[concat.reference]), concat.parts, concat.reference))
        if len(concat_sms[concat.reference]) == concat.parts:
            sortedParts = sorted(concat_sms[concat.reference].items())
            message = "".join([x[1] for x in sortedParts])
            del concat_sms[concat.reference]
    else:
        message = sms.text

    if message:
        print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, message))
        date = datetime.today().strftime('%Y%m%d%H%M%S%f')
        # Uncomment to save the SMS in a file
        #with open('/path/to/messages/' + date + '.txt', 'w') as the_file:
        #    the_file.write('{0}:{1}'.format(sms.number, sms.text))

   
  
fresult = ["0891421952804714F3440C914219125432650008023070115165808C050003820201062C0633062F0633062C06330641063300200633062F0633062C0633062F063300200633062F0633062C06330641063406410634062C0633062F00200633062F0633062C0633062F0633062F0633062C0634062F0633062F063406270633062C0633062C0633062F0633062C0633062F0633062F0633062C0633062F0633062F0633062C0633","0891421952804714F3440C914219125432650008023070115185803C05000382020206300633062C06330641063306410634062C0633062C063306410633062F0633062F063306410633062F0633062F0633062C0635062F"]

messages = []
for sms in fresult:

    smsDict = decodeSmsPdu(sms)
    nsms = sms = ReceivedSms( 0, smsDict['number'], smsDict['time'], smsDict['text'], smsDict['smsc'], smsDict.get('udh', []))
    messages.append(nsms)
index = 1
for massage in messages:
    handleSms(massage)

