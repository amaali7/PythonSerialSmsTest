import serial
import locale

ser = serial.Serial('/dev/ttyUSB3', baudrate=921600, timeout=None)
ser.flushInput()

while True:
    try:
        # ascii
        ser_bytes = ser.readline()
        sbuffer = ser_bytes.decode()
        dataS1 = sbuffer.split("⁁⁂⁁")
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
                    tc = da[4].split('"',1)
                    finalData = {
                        "Phone": da[1].replace('"',''),
                        "Date": da[3].replace('"',''),
                        "Time": tc[0],
                        "Content": tc[1].replace('\r\n', '').strip()
                    }
                    print(finalData)
        else:
            print(sbuffer)

    except Exception as e:
        print(e)
ser.close()