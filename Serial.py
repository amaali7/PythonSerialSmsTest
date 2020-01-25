import serial
import requests
from time import sleep
from threading import Thread
from multiprocessing import Process, Queue
from json import loads
from binascii import hexlify
from smspdu.codecs import UCS2

bord01 = serial.Serial('/dev/ttyUSB0', baudrate=921600, timeout=None)
bord01.flushInput()

sleep(1)
DataBySerial = Queue()
SerialRecived = Queue()
SerialToSend = Queue()


# Process 1

def Process1(T11, T12, Recived, Send):

    T_11 = Thread(target=T11, args=(Recived,))
    T_12 = Thread(target=T12, args=(Send, ))


    T_11.start()
    T_12.start()

    T_11.join()
    T_12.join()


# T11
def TakeDataFromSerial(queue):
    while True:
        try:
            # ascii
            ser_bytes = bord01.readline()
            sbuffer = ser_bytes.decode()
            queue.put(sbuffer)
            sleep(0.1)
        except: # Exception as e:
            pass # print(e)

# T21
def ManageRawData(queue1, queue2):
    while True:
        sleep(0.1)
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
                for idx, val in enumerate(fresult):
                    if idx == 0:
                        pass
                    else:
                        da = val.split(',')
                        tc = da[4].split('"', 1)
                        # finalData = {
                        #     "Phone": da[1].replace('"', ''),
                        #     "Date": da[3].replace('"', ''),
                        #     "Time": tc[0],
                        #     "Content": tc[1].replace('\r\n', '').strip()
                        # }
                        phone = UCS2.decode(da[1].replace('"', ''))
                        Content = UCS2.decode(tc[1].replace('\r\n'))

                        print(da[1])
                        finalData = {
                            "companyPhone": "0999991230",
                            "senderPhone": phone,
                            "messageContent": Content
                        }
                        queue2.put(finalData)
                        print('Data From Manage T12 : '+ str(finalData))
            elif dataS1[0] == "SmsSendReport":
                result = dataS1[1]
                fresult = result.split("⁂⁁⁂")
                print(f'Sms Status : {fresult[1]}  Index : {fresult[0]}')
            else:
                print(income)

# T23
def UploadOurData(queue1, queue2):
    while True:
        sleep(0.1)
        if not queue1.empty():
            data = queue1.get()
            payload = data
            r = requests.post('http://172.105.87.5/api/companies/displaymenuandoptions', json=payload,
                              headers={'Content-Type': 'application/json'})
            if r.status_code != '200':
                queue2.put(r.text)



# Process 2
def Process2(T21, T22, T23, Resave, Send):

    incomeSms = Queue()
    T_21 = Thread(target=T21, args=(Resave, incomeSms))
    T_22 = Thread(target=T22, args=(queue, ))

    T_21.start()
    T_22.start()

    T_21.join()
    T_22.join()

# T22
def DownloadData(queue):
        while True:
            sleep(0.1)
            payload = {
                'cellid': '1003',
            }
            r = requests.post('http://172.105.87.5/api/companies/getallsms', json=payload,
                             headers={'Content-Type': 'application/json'})
            if r.status_code == '200':
                queue.put(r.text)
                print('Data From Download T21 : ' + str(r.text))

# T22
def SendDataToSerial(queue):
    while True:
        sleep(0.1)
        if not queue.empty():
            res = loads(queue.get())
            recaver = UCS2.encode(res['smsReciver'])
            content = UCS2.encode(res['smsContent'])
            payload = "SendSms⁁⁂⁁0⁁⁂⁁123⁂⁁⁂" + "00"+recaver + "⁂⁁⁂"+ content
            print(payload)
            bord01.write(payload.encode())

P1 = Process(target=Process1, args=(TakeDataFromSerial, SendDataToSerial, SerialRecived, SerialToSend))
P2 = Process(target=Process2, args=(ManageRawData, DownloadData, UploadOurData, SerialRecived, SerialToSend))

P1.start()
P2.start()

P1.join()
P2.join()

bord01.close()