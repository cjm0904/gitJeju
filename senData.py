import serial
import myMqtt as mqtt
import time, json
import pymysql as sql


co2 = 0
temperature = 0
humidity = 0
i = 0
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
conn = sql.connect(host='127.0.0.1', user='root', password='ziumks', db='jeju', charset='utf8')
siteNm = 'T12'

def sensingData():
    i=0
    try:
        while True:
            try:
                data = ser.readline().decode('utf-8')
            except UnicodeDecodeError as e:
                continue
            if data.__len__() != 38:
                pass
            else:
                cNum = (data[0:4])
                rawCO2 = (data[4:12])
                rawTemp = (data[14:24])
                rawHumid = (data[26:34])
                co2 = (int(rawCO2[0:2])-0x30)*1000 + (int(rawCO2[2:4])-0x30) * 100 + (int(rawCO2[4:6])-0x30)*10 + (int(rawCO2[6:8])-0x30) 
                # temperature =  (int(rawTemp[0:2])-0x30)*100 + (int(rawTemp[2:4])-0x30)*10 + (int(rawTemp[4:6])-0x30) * 1 + (int(rawTemp[8:10])-0x30) * 0.1
                temperature = ((int(rawTemp[2:4])-0x30)*10 + (int(rawTemp[4:6])-0x30) * 1 + (int(rawTemp[8:10])-0x30) * 0.1)*10
                humidity = ((int(rawHumid[0:2])-0x30)*10 + (int(rawHumid[2:4])-0x30) *1 + (int(rawHumid[6:8])-0x30) * 0.1)*10
            
    #            print("co2 : " + str(co2))
    #            print("temperature : " + str(temperature))
    #            print("humid : " + str(humidity))
            
                now = round(time.time())
                result = {'id' : cNum,'t' : now,'t1': int(temperature), 't2': int(temperature), 'hm': int(humidity), 'co': int(co2), 'wn':00}
                print(result)

                qry = 'insert into jeju_sensor(id, area, time, humidity, temperature1, temperature2, co2, checking) values(%s, %s, %s, %s, %s, %s, %s, %s)'
                param = (i, 'jeju1', now, humidity,temperature, temperature, co2, 0)

                mqTopic = 'msr' + '/' + siteNm + '/' + cNum
    #            print(result)
                try:
                    mqtt.mqClient.publish(topic=mqTopic, payload=json.dumps(result), qos=0)
                    i = i+1
                except ConnectionError as e:
                    print("error : " + str(e))
                    pass

                try:
                    with conn.cursor() as cursor:
                        cursor.execute(qry, param)
                        conn.commit()
                except TypeError as e:
                    print(str(e))

    except KeyboardInterrupt:
        ser.close()


