import os
#from sqlite3.dbapi2 import Date
import sys
import random
# pip install pyqt5-tools
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from matplotlib.pyplot import get
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
from init import *
from agent import Mqtt_client 
import time
import numpy as np
from icecream import ic
from datetime import datetime 
import data_acq as da
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import paho.mqtt.client as mqtt
import logging

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.WARNING)

# define file handler and set formatter
file_handler = logging.FileHandler('logfile_gui.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

# Logs
# logger.debug('A debug message')
# logger.info('An info message')
# logger.warning('Something is not right.')
# logger.error('A Major error has happened.')
# logger.critical('Fatal error. Cannot continue')


global WatMet
WatMet=True
def time_format():
    return f'{datetime.now()}  GUI|> '
ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False) # use True for including script file context file 
# Creating Client name - should be unique 
global clientname
r=random.randrange(1,10000) # for creating unique client ID
clientname="IOT_clientId-nXLMZeDcjH"+str(r)
global CONNECTED
CONNECTED = False

button_topic = 'pr/home/button_123_YY/sts'

def check(fnk):    
    try:
        rz=fnk
    except:
        rz='NA'
    return rz        
     
      
class MC(Mqtt_client):
    def __init__(self):
        super().__init__()
    def on_message(self, client, userdata, msg):
            global WatMet
            topic=msg.topic            
            m_decode=str(msg.payload.decode("utf-8","ignore"))
            ic("message from:"+topic, m_decode)
            mainwin.statusDock.update_mess_win(da.timestamp()+'  :' + m_decode)



   
class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self,mc,dht,temp,airpressure):
        QDockWidget.__init__(self)        
        self.mc = mc
        self.topic = comm_topic+'#'        
        self.mc.set_on_connected_to_form(self.on_connected)        
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
           
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
      
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)        
        self.eConnectButton=QPushButton("Connect", self)
        self.eConnectButton.setToolTip("click me to connect")
        self.eConnectButton.clicked.connect(self.on_button_connect_click)
        self.eConnectButton.setStyleSheet("background-color: red")        
        formLayot=QFormLayout()
        formLayot.addRow("Host",self.eHostInput )
        formLayot.addRow("Port",self.ePort )        
        formLayot.addRow("",self.eConnectButton)
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect") 
        self.conected=False
        self.dht=dht
        self.temp=temp
        self.airpressure=airpressure
        
    def on_connected(self):
        self.eConnectButton.setStyleSheet("background-color: green")
        self.eConnectButton.setText('Connected')
        self.conected=True
      
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())           
        self.mc.connect_to()        
        self.mc.start_listening()
        self.dht.on_button_connect_click(self)
        self.temp.on_button_connect_click(self)
        self.airpressure.on_button_connect_click(self)
        time.sleep(1)
        if not self.mc.subscribed:
            self.mc.subscribe_to(self.topic)
            
class StatusDock(QDockWidget):
    """Status """
    def __init__(self,mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        self.boilerTemp = QLabel()
        self.boilerTemp.setText("80")
        self.boilerTemp.setStyleSheet("color: red")
        self.freezerTemp = QLabel()
        self.freezerTemp.setText("-5")
        self.freezerTemp.setStyleSheet("color: blue")
        self.fridgeTemp = QLabel()
        self.fridgeTemp.setText("4")
        self.fridgeTemp.setStyleSheet("color: green")
        self.wifi = QLabel()
        self.wifi.setText("Normal")
        self.wifi.setStyleSheet("color: green")
        self.door = QLabel()
        self.door.setText("Closed")
        self.door.setStyleSheet("color: green")
        self.eRecMess=QTextEdit()
        self.eSubscribeButton = QPushButton("Subscribe",self)
        self.eSubscribeButton.clicked.connect(self.on_button_subscribe_click)       
        formLayot=QFormLayout()        
        formLayot.addRow("Alarm Messages:",self.eRecMess)
        formLayot.addRow("",self.eSubscribeButton)                
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Status") 
        
    def on_button_subscribe_click(self):        
        self.mc.subscribe_to('alarm')
        self.eSubscribeButton.setStyleSheet("background-color: green")
    
    # create function that update text in received message window
    def update_mess_win(self,text):
        self.eRecMess.append(text)              
       
    def on_button_publish_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), self.eMessageBox.toPlainText())
        self.ePublishButton.setStyleSheet("background-color: yellow")
        
class GraphsDock(QDockWidget):
    """Graphs """
    def __init__(self,mc):
        QDockWidget.__init__(self)        
        self.mc = mc        
        self.eElectricityButton = QPushButton("Show",self)
        self.eElectricityButton.clicked.connect(self.on_button_Elec_click)        
        self.eElectricityText=QLineEdit()
        self.eElectricityText.setText(" ")
        self.eWaterButton = QPushButton("Show",self)
        self.eWaterButton.clicked.connect(self.on_button_water_click)        
        self.eWaterText= QLineEdit()
        self.eWaterText.setText(" ")
        self.eStartDate= QLineEdit()
        self.eEndDate= QLineEdit()
        self.eStartDate.setText('2023-06-08')
        self.eEndDate.setText('2023-06-10')
        self.eDateButton=QPushButton("Insert", self)
        self.eDateButton.clicked.connect(self.on_button_date_click)
        self.date=self.on_button_date_click
        formLayot=QFormLayout()       
        formLayot.addRow("all kicks",self.eElectricityButton)
        formLayot.addRow("air pressure",self.eWaterButton)
        formLayot.addRow("Start date: ", self.eStartDate)
        formLayot.addRow("End date: ", self.eEndDate)
        formLayot.addRow("", self.eDateButton)
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget)
        self.setWindowTitle("Graphs")
        self.stratDateStr= self.eStartDate.text()
        self.endDateStr= self.eEndDate.text()  
    
    def on_button_date_click (self):
        self.stratDateStr= self.eStartDate.text()
        self.endDateStr= self.eEndDate.text()        

    def on_button_water_click(self):
       self.stratDateStr= self.eStartDate.text()
       self.endDateStr= self.eEndDate.text()  
       self.update_plot(self.stratDateStr, self.endDateStr, 'air_sensor')       
       self.eWaterButton.setStyleSheet("background-color: yellow")

    def on_button_Elec_click(self):
        self.stratDateStr= self.eStartDate.text()
        self.endDateStr= self.eEndDate.text()  
        self.update_plot(self.stratDateStr, self.endDateStr,'kick_sensor' )
        self.eElectricityButton.setStyleSheet("background-color: yellow")

    def update_plot(self,date_st,date_end, meter):
        rez= da.filter_by_date(meter,date_st,date_end)
        timenow = []  
        y_axis = []       
        for row in rez:
            timenow.append(row[0])
            if meter=='kick_sensor':
                y_axis.append(row[2])
            else:
                y_axis.append(row[1])
        
        mainwin.plotsDock.plot(timenow, y_axis)
        mainwin.plotsDock.name_changing(meter) 


class PlotDock(QDockWidget):
    """Plots """
    def __init__(self):
        QDockWidget.__init__(self)        
        self.setWindowTitle("Plots")
        self.graphWidget = pg.PlotWidget()    
        self.setWidget(self.graphWidget)
        
        rez= da.filter_by_date('kick_sensor','2023-06-08','2023-06-10')  
     
        datal = []  
        timel = []        
        for row in rez:
           
            timel.append(row[0])
    
            datal.append(row[2])
           
        self.graphWidget.setBackground('b')
        # Add Title
        self.graphWidget.setTitle("kicks Timeline", color="w", size="15pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Value", **styles)
        self.graphWidget.setLabel("bottom", "Date", **styles)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        #self.graphWidget.setXRange(0, 10, padding=0)
        #self.graphWidget.setYRange(20, 55, padding=0)            
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line=self.graphWidget.plot( datal,  pen=pen)

    def plot(self, timel, datal):
        self.data_line.setData( datal)  # Update the data.
    def name_changing(self,name):
           self.graphWidget.setTitle(name+ "Timeline", color="w", size="15pt")
      
class ButtonDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
      
        
        self.ePushtbtn=QPushButton("GENERATE KICK", self)
        self.ePushtbtn.setToolTip("Push me")
        self.ePushtbtn.clicked.connect(self.push_button_click)
        self.ePushtbtn.setStyleSheet("background-color: red")

        self.ePublisherTopic=QLabel()
        self.ePublisherTopic.setText("kick-sensor")

        self.kickpower=QLabel()
        self.kickpower.setText("0")

        self.Durationt=QLabel()
        self.Durationt.setText("0")


        formLayot=QFormLayout()
        # formLayot.addRow("Host",self.eHostInput )
        # formLayot.addRow("Port",self.ePort )
        # formLayot.addRow("Client ID", self.eClientID)
        # formLayot.addRow("User Name",self.eUserName )
        # formLayot.addRow("Password",self.ePassword )
        # formLayot.addRow("Keep Alive",self.eKeepAlive )
        # formLayot.addRow("SSL",self.eSSL )
        # formLayot.addRow("Clean Session",self.eCleanSession )

       
        formLayot.addRow("Pub topic",self.ePublisherTopic)
        formLayot.addRow("kick power",self.kickpower)
        formLayot.addRow("duration",self.Durationt)
        formLayot.addRow("Button",self.ePushtbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("kick-dock") 
        self.conected=False
        self.duration=0
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
    def on_button_connect_click(self,connection):
        self.mc.set_broker(connection.eHostInput.text())
        self.mc.set_port(int(connection.ePort.text()))
        self.mc.set_clientName(connection.eClientID.text())
        self.mc.set_username(connection.eUserName.text())
        self.mc.set_password(connection.ePassword.text()) 
              
        self.mc.connect_to()        
        self.mc.start_listening()

        self.conected=True
        

    def push_button_click(self):

        if self.conected:
            self.ePushtbtn.setStyleSheet("background-color: green")
            self.ePushtbtn.setEnabled(False)
            self.powerkicked=random.randrange(1,10)
            self.duration=self.powerkicked*3
            self.kickpower.setText(str(self.powerkicked))
            self.Durationt.setText(str(self.duration))
            self.mc.publish_to(self.ePublisherTopic.text(), '"value":'+str(self.powerkicked)+"duration:"+str(self.duration))
            
class SpeedTime(QDockWidget):
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
       
        
        self.ePublisherTopic=QLabel()
        self.ePublisherTopic.setText("speed-time-sensor")

        self.speed=QLineEdit()
        self.speed.setText('0')

        self.time=QLineEdit()
        self.time.setText('0')

        formLayot=QFormLayout()       
       
        formLayot.addRow("Pub topic",self.ePublisherTopic)
        formLayot.addRow("speed",self.speed)
        formLayot.addRow("time",self.time)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("speed-time dock")
        self.now=0 

    def generate_linear(self, duration):
        t = np.linspace(0, duration, 1000)
        y = 1 - (t / duration)  # Linear function starting from 1 and going down to 0
        return t, y

    
    def get_y_at_x(self,x, x_values, y_values):
        index = np.searchsorted(x_values, x)  # Find the index of the closest x value
        if index == 0:
            return y_values[0]  # If x is before the first recorded value, return the first y value
        if index == len(x_values):
            return y_values[-1]  # If x is after the last recorded value, return the last y value
        x1 = x_values[index - 1]
        x2 = x_values[index]
        y1 = y_values[index - 1]
        y2 = y_values[index]
        interpolated_y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)  # Linear interpolation formula
        return interpolated_y

    def update_data(self, tempdoc):
        if tempdoc.duration > 0 :
            self.Time = tempdoc.duration  # Duration of the graph
            t, y = self.generate_linear(self.Time)
            self.now += 1
            specific_time = self.now 
            if specific_time <= self.Time:
                self.specific_amplitude = self.get_y_at_x(specific_time, t, y) * 50
                self.specific_amplitude =round(self.specific_amplitude,2)
                current_data = 'speed: ' + str(self.specific_amplitude) + ' time since the ball kicked: ' + str(self.now)
                self.time.setText(str(self.now))
                self.speed.setText(str(self.specific_amplitude))
                self.mc.publish_to("speed-time-sensor", current_data)
                
            else:
                tempdoc.duration=0
                self.now=0
                tempdoc.ePushtbtn.setStyleSheet("background-color: red")
                tempdoc.ePushtbtn.setEnabled(True)

            
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self,connection):
        self.mc.set_broker(connection.eHostInput.text())
        self.mc.set_port(int(connection.ePort.text()))
        self.mc.set_clientName(connection.eClientID.text())
        self.mc.set_username(connection.eUserName.text())
        self.mc.set_password(connection.ePassword.text()) 
              
        self.mc.connect_to()        
        self.mc.start_listening()

    def push_button_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":1')
      
class AirPressur(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
      
        
        self.ePushtbtn=QPushButton("INFLATE", self)
        self.ePushtbtn.setToolTip("Push me")
        self.ePushtbtn.clicked.connect(self.push_button_click)
        self.ePushtbtn.setStyleSheet("background-color: red")

        self.ePublisherTopic=QLabel()
        self.ePublisherTopic.setText("airpressure-sensor")
        
        self.airp=11.6
        self.AirPresurenow=QLabel()
        self.AirPresurenow.setText(str(self.airp))

        formLayot=QFormLayout()
        # formLayot.addRow("Host",self.eHostInput )
        # formLayot.addRow("Port",self.ePort )
        # formLayot.addRow("Client ID", self.eClientID)
        # formLayot.addRow("User Name",self.eUserName )
        # formLayot.addRow("Password",self.ePassword )
        # formLayot.addRow("Keep Alive",self.eKeepAlive )
        # formLayot.addRow("SSL",self.eSSL )
        # formLayot.addRow("Clean Session",self.eCleanSession )

        
        formLayot.addRow("Pub topic",self.ePublisherTopic)
        formLayot.addRow("Air Pressure (psi)",self.AirPresurenow)
        formLayot.addRow("Button",self.ePushtbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Air Pressure dock")
    def update_data(self):
        if self.airp>8.6:
            self.airp=self.airp-0.01
            self.airp=round(self.airp,2)
            self.mc.publish_to(self.ePublisherTopic.text(), '"value":'+str(self.airp))
            self.AirPresurenow.setText(str(self.airp))
            self.ePushtbtn.setStyleSheet("background-color: green")
        else:
            if self.airp>0:
                self.airp=self.airp-0.01
                self.AirPresurenow.setText(str(self.airp))
            self.mc.publish_to(self.ePublisherTopic.text(), '"value":'+str(self.airp))
            self.ePushtbtn.setStyleSheet("background-color: red")
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
    def on_button_connect_click(self,connection):
            self.mc.set_broker(connection.eHostInput.text())
            self.mc.set_port(int(connection.ePort.text()))
            self.mc.set_clientName(connection.eClientID.text())
            self.mc.set_username(connection.eUserName.text())
            self.mc.set_password(connection.ePassword.text()) 
                
            self.mc.connect_to()        
            self.mc.start_listening()


    def push_button_click(self):
        self.ePushtbtn.setStyleSheet("background-color: green")
        self.airp=11.6
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":'+str(self.airp))
        self.AirPresurenow.setText(str(self.airp))


class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)                
        # Init of Mqtt_client class
        # self.mc=Mqtt_client()
        self.mc=MC()        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('System GUI')
        # Init QDockWidget objects        
          
        self.statusDock = StatusDock(self.mc)
        
        self.tempDock = ButtonDock(self.mc)
        
        self.graphsDock = GraphsDock(self.mc)
        self.speed_time= SpeedTime(self.mc)
        
        self.plotsDock = PlotDock()
       
        self.AirPresure=AirPressur(self.mc)
        
        self.connectionDock = ConnectionDock(self.mc,self.speed_time,self.tempDock,self.AirPresure)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.tempDock)
        self.addDockWidget(Qt.TopDockWidgetArea, self.speed_time)
        self.addDockWidget(Qt.TopDockWidgetArea, self.AirPresure)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.statusDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.graphsDock)
       
        self.addDockWidget(Qt.BottomDockWidgetArea, self.plotsDock)
      
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000) 
        self.timera = QtCore.QTimer(self)
        self.timera.timeout.connect(self.update_dataa)
        self.timera.start(7000)
    def update_data(self):
        if self.connectionDock.conected: 
            self.speed_time.update_data(self.tempDock)
          
    def update_dataa(self):
        if self.connectionDock.conected: 
            self.AirPresure.update_data()
         

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()

    except:
        logger.exception("GUI Crash!")
