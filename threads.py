
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from smsappapi import *



x = API_Handler()

class getNumberThread(QThread):
    thread_signal = pyqtSignal(str)
    data_signal = pyqtSignal(tuple)
    stop_generate_signal = pyqtSignal()
    
    def __init__(self,service):
        super().__init__()
        self.service = service
        
    def run(self):
        
        self.x = API_Handler()
        self.x.signal_sender.connect(self.signal_handle)
        self.stop_generate_signal.connect(self.stopGenerating)
        # try:
        number_data = self.x.getNumber(service=self.service)
        
        if type(number_data)==tuple:
            self.data_signal.emit(number_data)
        else:
            self.thread_signal.emit("Can't Find Numbers Now")
        
    def signal_handle(self,msg):
        self.thread_signal.emit(msg)
        
    def stopGenerating(self):
        self.x.stopNumberGenerating()
                
class getBalaceThread(QThread):
    thread_signal = pyqtSignal(str)
    balance_signal = pyqtSignal(str)
    def run(self):
        
        x = API_Handler()
        x.signal_sender.connect(self.signal_handle)
        try:
            balance = x.getBalance()
            self.balance_signal.emit(str(balance))
        except:
            pass
        
    def signal_handle(self,msg):
        self.thread_signal.emit(msg)
        
class setStatusThread(QThread):
    response_singal = pyqtSignal(str)
    
    def __init__(self,number_id):
        super().__init__()
        self.number_id = number_id
    
    def run(self):
        
        try:
            res = x.setStatus(self.number_id,8)
            self.response_singal.emit(res)
        except:
            self.response_singal.emit('No Internet')
        
        
class numberHandleThread(QObject):
    
    time_update = pyqtSignal(str,int)
    status_signal = pyqtSignal(str,int)
        
    def __init__(self,number_id,index_in_list,rem_time):
        super().__init__()
        self.number_id = number_id
        self.number_index = index_in_list
        self.rem_time = rem_time
        
    def run(self):
            
        # Timer
        self.current_time = self.rem_time
        self.time_update.emit(str(self.current_time),self.number_index)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(60000)
        
        self.status_signal.emit('Waiting Code...',self.number_index)
        # Looking for Code
        self.codeTimer = QTimer()
        self.codeTimer.timeout.connect(self.getCodeStatus)
        self.codeTimer.start(2000)
        
        self.uthread = getStatusThread(self.number_id,self.number_index)
        self.uthread.status_signal.connect(self.sendStatus)
        
    def updateTime(self):
        if self.current_time in ['unknown','See Time on Website']:
            self.current_time = 'See Time on Website'
        else:
            self.current_time-=1
        self.time_update.emit(str(self.current_time),self.number_index)
        
    def getCodeStatus(self):
        self.uthread.start()
        
    def sendStatus(self,msg,index):
        
        self.timer.stop()
        self.codeTimer.stop()  
        self.status_signal.emit(msg,index)
        
    def stopUpdate(self):
        self.timer.stop()
        self.codeTimer.stop()  
            
class getStatusThread(QThread):
    
    status_signal = pyqtSignal(str,int)
        
    def __init__(self,number_id,index_in_list):
        super().__init__()
        self.number_id = number_id
        self.number_index = index_in_list
    def run(self):
        try:
            msg = x.getStatus(self.number_id)
            
            print(f'{msg} ,{self.number_id}')
            if 'STATUS_OK' in msg:
                self.status_signal.emit(msg,self.number_index)
            elif 'STATUS_WAIT_CODE' in msg:
                pass
                
            elif 'STATUS_CANCEL' in msg:
                self.status_signal.emit(msg,self.number_index)
            else:
                self.status_signal.emit(msg,self.number_index)
        except:
            
            self.status_signal.emit('No Internet',self.number_index)
            
class getCurrentActivationThread(QThread):
    status_signal = pyqtSignal(list,list)
    
    def run(self):
        # Status for waiting code numbers
        self.waiting_numbers = x.getCurrentActivationsList(0,50)
        # Status for received code numbers
        self.received_sms_numbers = x.getCurrentActivationsList(3,50)
        self.status_signal.emit(self.waiting_numbers,self.received_sms_numbers)
        
class searchTargetThread(QThread):
    countries = pyqtSignal(list)
    update = pyqtSignal()
    def run (self):
        self.api = API_Handler()
        self.api.countries_signal.connect(self.sendCountries)
        # try:
        self.api.searchTargetNumbers(service='Amazon')
    # except:
        self.stopSearch()
        self.update.emit()
            
         
    def sendCountries(self,mycountries):
        self.countries.emit(mycountries)
    
    def stopSearch(self):
        self.api.stopSearchingCountries()