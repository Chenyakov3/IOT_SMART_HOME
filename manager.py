# intended to manage the Smart Home system
# insert data to Smart home DB

import paho.mqtt.client as mqtt
# import os
import time
# import sys, getopt
# import logging
# import queue
import random
from init import *
import data_acq as da
from icecream import ic
from datetime import datetime 

def time_format():
    return f'{datetime.now()}  Manager|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False) # use True for including script file context file  

# Define callback functions
def on_log(client, userdata, level, buf):
        ic("log: "+buf)
            
def on_connect(client, userdata, flags, rc):    
    if rc==0:
        ic("connected OK")                
    else:
        ic("Bad connection Returned code=",rc)
        
def on_disconnect(client, userdata, flags, rc=0):    
    ic("DisConnected result code "+str(rc))
        
def on_message(client, userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    ic("message from: " + topic, m_decode)
    insert_DB(topic, m_decode)

def send_msg(client, topic, message):
    ic("Sending message: " + message)
    #tnow=time.localtime(time.time())
    client.publish(topic,message)   

def client_init(cname):
    r=random.randrange(1,10000000)
    ID=str(cname+str(r+21))
    client = mqtt.Client(ID, clean_session=True) # create new client instance
    # define callback function       
    client.on_connect=on_connect  #bind callback function
    client.on_disconnect=on_disconnect
    client.on_log=on_log
    client.on_message=on_message        
    if username !="":
        client.username_pw_set(username, password)        
    ic("Connecting to broker ",broker_ip)
    client.connect(broker_ip,int(port))     #connect to broker
    return client

def insert_DB(topic, m_decode):
    if topic == 'kick-sensor': 
        val=m_decode.split('"value":')[1].split('duration:')[0]
        dur=m_decode.split('duration:')[1]
        da.create_IOT_dev(da.timestamp(),dur,val) 
    elif  topic== 'speed-time-sensor':        
        speed=m_decode.split("speed:")[1].split(' time since the ball kicked: ')[0] 
        da.create_IOT_dev1(da.timestamp(),speed)
    elif topic=='airpressure-sensor':
        valu=m_decode.split('"value":')[1]
        da.create_IOT_dev2(da.timestamp(),valu)



def check_DB_for_change(client,lentuple):
    
    df = da.fetch_data(db_name, 'kick_sensor')
    lenpower=len(df.power)
    if lenpower!=lentuple[0]:
        if float(df.power[len(df.power)-1]) > 5:
            msg = 'very good kick youre so strong: '+str(df.power[len(df.power)-1])
            ic(msg)
            client.publish('alarm', msg)
        else:
            msg = "didn't you ate today you can do it stronger than:"+str(df.power[len(df.power)-1])
            ic(msg)
            client.publish('alarm', msg)

    df = da.fetch_data(db_name, 'air_sensor')
    if  len(df.psi)!=lentuple[1]:
        if float(df.psi[len(df.psi)-1]) >8.6:
            msg = 'Current air pressure is good '+ str(df.psi[len(df.psi)-1])
            ic(msg)
            client.publish('alarm', msg)
        else:
            msg = 'Current air pressure is bad '+ str(df.psi[len(df.psi)-1])+'please inflate '
            ic(msg)
            client.publish('alarm', msg)

    return(lenpower,len(df.psi))



def main():  
    lentuple=(len(da.fetch_data(db_name, 'kick_sensor')),len(da.fetch_data(db_name, 'air_sensor')))
   
    cname = "Manager-"
    client = client_init(cname)
    # main monitoring loop
    client.loop_start()  # Start loop
    client.subscribe('speed-time-sensor')
    client.subscribe('kick-sensor')
    client.subscribe('airpressure-sensor')
    try:
        while conn_time==0:  
            lentuple=check_DB_for_change(client,lentuple)
            time.sleep(conn_time+10)      
        ic("con_time ending") 
    except KeyboardInterrupt:
        client.disconnect() # disconnect from broker
        ic("interrrupted by keyboard")

    client.loop_stop()    #Stop loop
    # end session
    client.disconnect() # disconnect from broker
    ic("End manager run script")

if __name__ == "__main__":
    main()
