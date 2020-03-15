import serial
import requests
from time import sleep
from threading import Thread
from multiprocessing import Process, Queue
from json import loads
from pdu import encodeSmsSubmitPdu, decodeSmsPdu
import abc

from utilty import handleSms, Sms, ReceivedSms

bord01 = serial.Serial('/dev/ttyUSB0', baudrate=921600, timeout=None)
bord01.flushInput()

sleep(1)
esp32ToPc = Queue()
pcToEsp32 = Queue()



# Process group 1
def process_1(fromesp32, toesp32, esp32topc, pctoesp32):
    # process 1 manage serial data in and out using :
    # esp32ToPc & pcToEsp32 Queue to exchange data with other procsess
    t_fromesp32 = Thread(target=fromesp32, args=(esp32topc,))
    t_toesp32 = Thread(target=toesp32, args=(pctoesp32,))

    t_fromesp32.start()
    t_toesp32.start()

    t_fromesp32.join()
    t_toesp32.join()

# Thread one in group 1
def fromEsp32(queue):
    while True:
        try:
            # ascii
            sbuffer = bord01.readline().decode()
            queue.put(sbuffer)
            sleep(0.001)
        except:  # Exception as e:
            pass  # print(e)

# Thread two in group 1
def toEsp32(queue):
    while True:
        sleep(0.001)
        if not queue.empty():
            res = loads(queue.get())
            recaver = res['smsReciver']
            content = res['smsContent']
            smsPduPayload = encodeSmsSubmitPdu(recaver, content)
            mPayload = "SendSms⁁⁂⁁0⁁⁂⁁123⁁⁂⁁1⁂⁁⁂"+ len(smsPduPayload) + "⁁⁂⁁"
            for idx, val in enumerate(smsPduPayload):
                if len(smsPduPayload)>1:
                    if idx == 0:
                        payload = mPayload + idx + "⁂⁁⁂" + val.tpduLength + "⁂⁁⁂" + val
                    else:
                        payload += "⁁⁂⁁" + idx + "⁂⁁⁂" + val.tpduLength + "⁂⁁⁂" + val
                else:
                    payload = "SendSms⁁⁂⁁0⁁⁂⁁123⁁⁂⁁0⁂⁁⁂"+ val.tpduLength + "⁂⁁⁂" + val
                            
            print(payload)
            bord01.write(payload.encode())


# process group 2
def process_2(manageserialfromesp32, smsresponce, rotaincheck, esp32topc, pctoesp32):
    # process 2 manage data from esp32ToPc Queue & send data to our online server
    smsresponcequeue = Queue()
    t_manageserialfromesp32 = Thread(target=manageserialfromesp32, args=(esp32topc, smsresponcequeue))
    t_smsresponce = Thread(target=smsresponce, args=(smsresponcequeue, pctoesp32))
    t_rotaincheck = Thread(target=rotaincheck, args=(pctoesp32,))

    t_manageserialfromesp32.start()
    t_smsresponce.start()
    t_rotaincheck.start()

    t_manageserialfromesp32.join()
    t_smsresponce.join()
    t_rotaincheck.join()

# Thread one in group 2
def manageSerialFromEsp32(queue1, queue2):
    while True:
        sleep(0.001)
        if not queue1.empty():
            income = queue1.get()
            dataS1 = income.split("⁁⁂⁁")
            if dataS1[0] == "StatusReport":
                result = dataS1[1]
                fresult = result.split("⁂⁁⁂")
                print(f'Report : [{fresult[0]}] Status : [{fresult[1].strip()}]')
            elif dataS1[0] == "NewSms":
                result = dataS1[1]
                # print(f'Sms List is : {result}')
                fresult = result.split("⁂⁁⁂")
                messages = []
                if fresult.pop(0) == 0:
                    for sms in fresult:
                        smsDict = decodeSmsPdu(sms)
                        nsms = ReceivedSms( 0, smsDict['number'], smsDict['time'], smsDict['text'], smsDict['smsc'], smsDict.get('udh', []))
                        messages.append(nsms)
                    for massage in messages:
                        newM =  handleSms(massage)   
                
            elif dataS1[0] == "SmsSendReport":
                result = dataS1[1]
                fresult = result.split("⁂⁁⁂")
                print(f'Sms Status : {fresult[1]}  Index : {fresult[0]}')
            else:
                print(income)

# Thread two in group 2
def smsResponce(queue1, queue2):
    while True:
        sleep(0.001)
        if not queue1.empty():
            data = queue1.get()
            payload = data
            r = requests.post('http://172.105.87.5/api/companies/displaymenuandoptions', json=payload,
                              headers={'Content-Type': 'application/json'})
            if r.status_code != '200':
                queue2.put(r.text)


# Thread three in group 2
def rotainCheck(queue):
    while True:
        sleep(0.001)
        payload = {
            'cellid': '1003',
        }
        r = requests.post('http://172.105.87.5/api/companies/getallsms', json=payload,
                          headers={'Content-Type': 'application/json'})
        if r.status_code == '200':
            queue.put(r.text)


P1 = Process(target=process_1, args=(fromEsp32, toEsp32, esp32ToPc, pcToEsp32))
P2 = Process(target=process_2, args=(manageSerialFromEsp32, smsResponce, rotainCheck, esp32ToPc, pcToEsp32))

P1.start()
P2.start()

P1.join()
P2.join()

bord01.close()