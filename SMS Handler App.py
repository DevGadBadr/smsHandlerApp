
# This is a script to Handle SMS Service using API
# Dev Gad Badr © All Rights Reserved

import time
import pyotp
import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from app import Ui_Dialog
from otpsWindow import Ui_otpwin
from PyQt5 import QtCore, QtGui, QtWidgets
from smsappapi import *
import sys
import json
import bcrypt
from cryptography.fernet import Fernet
from threads import *
import socket

class myview(Ui_Dialog):
    def startview(self,window):
        super().setupUi(window)
        window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
        window.setWindowTitle('SMS Handler')
        self.myedit()
        self.OTPsWindow()
                

    def myedit(self):
        self.quickOtpsButton.clicked.connect(self.OTPsWindow)
        self.closeButton.clicked.connect(wind.close)
        self.quickOtpsButton.setCursor(Qt.PointingHandCursor)
        self.closeButton.setCursor(Qt.PointingHandCursor)
        
    def OTPsWindow(self):
        
        
        class updatedOTPsWindow(Ui_otpwin):
            
            
            def normalView(self,windo):
                super().setupUi(windo)
                windo.setWindowFlags(windo.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                windo.setWindowFlags(windo.windowFlags() | Qt.WindowMinimizeButtonHint)
                windo.setWindowFlags(windo.windowFlags() | Qt.WindowMaximizeButtonHint)
                
                self.update_butt.clicked.connect(self.getnewNumberHandle)
                
                self.service_field.textChanged.connect(self.addserviceHandle)
                windo.finished.connect(self.cleanClose)
                self.close_button.clicked.connect(windo.close)
                otps_window.setWindowTitle('SMS Numbers Handler')
                today = datetime.date.today()
                year = today.year
                self.labell = QtWidgets.QLabel(windo)
                
                self.labell.setText(f'Dev Gad Badr © All Rights Reserved {year}, For Mr Mounir')
                self.labell.setStyleSheet('color:grey')
                self.listWidget.hide()
                # To Be Adjusted
                self.current_number_of_rows = 1
                
                # To Be Adjusted
                row_object ={
                    'row_number':1,
                    'number_field':self.number_field_1,
                    'number_copy':self.number_copy_btn_1,
                    'code_field':self.code_field_1,
                    'code_copy':self.code_copy_but_1,
                    'country':self.country_name_1,
                    'service':self.servic_name_1,
                    'status':self.code_status_1,
                    'cancel':self.cancel_number_but_1,
                    'label':self.label_1,
                    'label2':self.label_2_1,
                    'container':self.single_container,
                    'number_id':'',
                    'handler':''
                }
               
                self.current_rows = [row_object]
                self.readServices()
                self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.listWidget.itemClicked.connect(self.itemselected)
                
                self.cancel_confirm_but.clicked.connect(self.cancelConfirmed)
                self.close_cancel_widget.clicked.connect(lambda: self.cancel_confirm.hide())
                self.messages.clear()
                
                # self.gridLayoutWidget.setStyleSheet('background-color:black')
                self.modifyView()
                self.assignCopyButtons()
                # self.settings_widget.hide()
                self.pass_widget.hide()
                self.setting_button.clicked.connect(self.settingsHandle)   
                self.pass_widget_hidden = True
                self.password_field.setEchoMode(QLineEdit.Password)
                self.password_change_field.setEchoMode(QLineEdit.Password)
                self.setting_save_but.clicked.connect(self.save_settings)
                self.settings_widget.hide()
                self.setting_cancel_but.clicked.connect(lambda: self.settings_widget.hide())
                self.close_notify.clicked.connect(lambda: self.number_notification.hide())
                self.timesNumber.textChanged.connect(self.setTimesNumber)
                self.saved_widget.hide()
                self.assignCancelButtons()
                
                # Initials
                with open('CountryCodes.json','r') as c:
                    self.country_codes = json.load(c)
                c.close()
                self.target_countries = searchTargetThread()
                self.target_countries.countries.connect(self.updateAvailableCountries)
                self.target_countries.update.connect(self.refresh)

                self.readTargetCountries()
                
                # Resize
                self.scrollArea.setWidgetResizable(False)
                self.labell.setGeometry(340,830,500,60)
                self.cancel_width = self.cancel_number_but_1.width()+self.code_status_1.width()
                self.cancel_confirm.setGeometry(QtCore.QRect(463, 45, self.cancel_number_but_1.width()+self.code_status_1.width(), 30))
                
                # Hidden
                self.number_notification.hide()
                self.cancel_confirm.hide()
                self.listWidget.hide()
                
                # Creating some Timers
                self.con_timer = QTimer()
                self.con_timer.timeout.connect(self.checkForConnectionBack)
                self.q = QTimer()
                
                self.checkConnection()
                
                if self.no_connection:
                    self.label_25.setText('You are Offline.')
                    self.update_butt.setDisabled(True)
                    self.messages.clear()
                    self.handleMessages('Connection Lost')
                    self.con_timer.start(5000)
                    
                else:
                    self.target_countries.start()
                    self.readLastView()
                    
                self.label_17.clear()
                self.removeRowHandle(1)
                self.running_threads = []
                self.installOTP()
                
            def refresh(self):
                self.close_button.click()
                n.otpsWindowCLosed()
                time.sleep(2)
            def readTargetCountries(self):
                with open('target_countries.txt','r') as g:
                    n = g.readlines()
                    clean=[]
                    for i in n:
                        f = i.replace('\n','')
                        clean.append(f)
                g.close
                self.listWidget_2.clear()
                for item in list(set(clean)):
                    self.listWidget_2.addItem(item)
                    
            def updateAvailableCountries(self,countries_list):
                print(f'updating countries list')
                self.readTargetCountries()
                                    
            def setTimesNumber(self):
                entered_text = self.timesNumber.text()
                if entered_text=='':
                    pass
                else:
                    try:
                        if not int(entered_text)<=8 :
                            self.timesNumber.setText('8')
                        elif '0' in entered_text:
                            self.timesNumber.setText('1') 
                    
                    except:
                        self.timesNumber.setText('1') 
                    
            def checkConnection(self):
                try:
                    socket.create_connection(("8.8.8.8", 53), timeout=5)
                    self.no_connection = False
                except OSError:
                    self.no_connection = True
                    
            def getbalance(self):
                
                self.label_17.clear()
                self.gb = getBalaceThread()
                self.gb.balance_signal.connect(self.setbalance)
                self.gb.thread_signal.connect(self.handleMessages)
                self.gb.start()
                
            def setbalance(self,balance):
                
                self.label_17.clear()
                try:
                    self.current_balance = float(balance)
                    print(self.current_balance)
                    self.label_17.setText(balance)
                except ValueError:
                    pass
                
                try:
                    if self.number_generated:
                        self.numberGeneratedMsg()
                except AttributeError:
                    pass
                
                
            def handleMessages(self,event):
                
                if self.q.isActive():
                    self.q.killTimer(self.qstarter)
                self.messages.show()
                self.messages.setText(event)
                if 'Getting Balance' in event:
                    self.qstarter = self.q.singleShot(3000,lambda: self.messages.clear())
                else:
                    self.qstarter = self.q.singleShot(6000,lambda: self.messages.clear())
                        
            def assignCancelButtons(self):
                
                for rowobject in self.current_rows:
                    try:
                        rowobject['cancel'].clicked.disconnect(self.cancelNumberHandle)  
                    except:
                        pass
                
                for rowobject in self.current_rows:
                    rowobject['cancel'].clicked.connect(self.cancelNumberHandle)
            
            def cancelNumberHandle(self):
                but_clicked = self.gridLayoutWidget.sender().objectName().split('_')[-1]
                self.row_index = int(but_clicked)  
                
                for index,item in enumerate(self.current_rows):
                    if item['row_number']==self.row_index:
                        row_to_remove = item
                        self.index_in_list = index
                        break
                self.cancelConfirm(self.index_in_list)
                
            def cancelConfirm(self,index_in_list):

                self.cancel_confirm.setGeometry(QtCore.QRect(self.current_rows[index_in_list]['status'].x(), self.current_rows[index_in_list]['cancel'].y()+10,((self.current_rows[index_in_list]['cancel'].x()+40)-self.current_rows[index_in_list]['status'].x()+20), 30))
                self.close_cancel_widget.setGeometry(QRect(380, 0, 40, 30))
                self.cancel_confirm.show()
                
                
            def cancelConfirmed(self):
                
                self.cancel_number(self.current_rows[self.index_in_list]['number_id'])
                
            def save_settings(self):
                api_key = self.api_field.text()
                self.max_cost = self.max_cost_field.text()
                password = self.password_change_field.text()
                
                # Encryption Passsword
                pass_salt =  bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), pass_salt)
                # max cost
                key = Fernet.generate_key()
                cipher_suite = Fernet(key)
                encrypted_number = cipher_suite.encrypt(str(self.max_cost).encode('utf-8'))

                config = {
                    "data": pass_salt.decode('utf-8'),
                    "data2": hashed_password.decode('utf-8'),
                    "data3": key.decode('utf-8'),
                    "data4": encrypted_number.decode('utf-8'),
                    "Author":"Developer and Engineer Gad Badr",
                    "Credits To":"Mr Mounir",
                    "Version":1,
                    "Encryption":"utf-8",
                    "lastservice":"Amazon",
                    "password":"encrypted",
                    "api-key":api_key
                }
                with open('config.json','w') as c:
                    json.dump(config,c)
                c.close()
                
                self.settings_widget.hide()
                self.saved_widget.show()
                self.saved_timer = QTimer()
                self.saved_timer.singleShot(1500,lambda: self.saved_widget.hide())     
                
                with open('target_countries.txt','w') as c:
                    c.write('')
                c.close()
                self.updateSearch()
                               
            
            def updateSearch(self):
                self.target_countries.stopSearch()
                print('Starting again to search')
                j = open('config.json','r') 
                m = json.load(j)
                m['count'] = 0
                f = open('config.json','w')
                json.dump(m,f)
                self.target_countries = searchTargetThread()
                self.target_countries.countries.connect(self.updateAvailableCountries)
                self.target_countries.start()
                            
            def modifyView(self):
                self.verScroll = self.scrollArea.verticalScrollBar()
                self.opacity_effect = QGraphicsOpacityEffect() 
                self.opacity_effect.setOpacity(0.2)
                self.verScroll.setGraphicsEffect(self.opacity_effect)
                m = open('config.json','r')
                n = json.load(m)
                servicee = n['lastservice']
                self.secret_field_1.setText(n['secret'])
                self.timesNumber.setText(n['no_times'])
                self.service_field.setText(servicee)
                self.update_butt.setCursor(Qt.PointingHandCursor)
                self.close_button.setCursor(Qt.PointingHandCursor)
                self.setting_button.setCursor(Qt.PointingHandCursor)
                self.access_setting_but.setCursor(Qt.PointingHandCursor)
                self.setting_save_but.setCursor(Qt.PointingHandCursor)
                self.cancel_confirm.setCursor(Qt.PointingHandCursor)
                self.balance_widget.setCursor(Qt.PointingHandCursor)
                self.number_generated = False
                self.balance_widget.clicked.connect(self.getbalance)
                
                                        
            def settingsHandle(self):
                self.access_setting_but.clicked.connect(self.accessSettingHandle)
                if self.pass_widget_hidden:
                    self.password_field.clear()
                    self.pass_widget.show()
                    self.pass_widget_hidden = False
                else:
                    self.pass_widget.hide()
                    self.pass_widget_hidden = True
                    
            def accessSettingHandle(self):
                password = self.password_field.text()
                with open('config.json','r') as r:
                    n = json.load(r)
                    readed_salt = n['data']
                    actual_hashed_password = n['data2'].encode('utf-8')
                    given_password_hashed = bcrypt.hashpw(password.encode('utf-8'), readed_salt.encode('utf-8'))
                    key = n['data3']
                    enc_number = n['data4']
                    api = n['api-key']
                r.close()
                
                if actual_hashed_password == given_password_hashed:
                    self.pass_widget.hide()
                    self.settings_widget.show()
                    self.password_field.clear()
                    self.pass_widget_hidden = True
                    self.password_change_field.setText(password)   
                    cipher_suite = Fernet(key)
                    decrypted_number = cipher_suite.decrypt(enc_number).decode('utf-8')
                    self.max_cost_field.setText(decrypted_number)
                    self.api_field.setText(api)
                    
                else:
                    self.password_field.setEchoMode(QLineEdit.Normal)
                    self.password_field.setText('Wrong Password')
                    self.wrong_pass_timer = QTimer()
                    self.wrong_pass_timer.timeout.connect(self.wrong_password)
                    self.wrong_pass_timer.singleShot(1500,self.wrong_password)
                    
            def wrong_password(self):
                self.password_field.clear()
                self.password_field.setEchoMode(QLineEdit.Password)
                                                                
            def readServices(self):
                n = open('services.txt','r',encoding='utf-8')
                f = n.read().split('\n')
                f = [x for x in f if x!='']
                self.m=[]
                n=0
                for tr in range(0,len(f)):
                    self.m.append(f[n+2]) 
                    n+=3
                    if n+3 >= len(f):
                        self.m.append(f[n+2]) 
                        break
                
                for item in self.m:
                    self.listWidget.addItem(item)
                
            def itemselected(self,event):
                
                self.service_field.setText(event.text())
                self.listWidget.hide()
                self.service_field.clearFocus()
                if self.service_field.text() in self.m:
                    self.valid_service = True
                else:
                    self.valid_service = False
                    self.service_field.clear()
                
            def addserviceHandle(self,event):
                text = event
                self.listWidget.clear()
                new_items = []
                for items in self.m:
                    if text.lower() in items.lower():
                        if items[0:len(event)].lower() == text.lower():
                            new_items.append(items)
                
                if len(new_items)>1:
                    for item in new_items:
                        self.listWidget.addItem(item)
                    
                    self.listWidget.show()
                else:
                    self.listWidget.hide()

            def getnewNumberHandle(self):
                
                self.checkConnection()
                try:
                    self.generate_times = int(self.timesNumber.text())
                except:
                    self.generate_times = 1
                    self.timesNumber.setText('1')
                    
                if self.no_connection:
                    self.label_25.setText('You are Offline.')
                    self.update_butt.setDisabled(True)
                    self.handleMessages('Connection Lost')
                    self.body_widget.show()
                    self.con_timer.start(5000)
                    
                else:
                    self.service = self.service_field.text()
                    
                    if self.service in self.m:
                        try:
                            self.prevoius_balance = float(self.label_17.text())
                        except ValueError:
                            pass
                        
                        self.workers=[]
                        for n in range(0,self.generate_times):
                            self.worker = getNumberThread(self.service)
                            self.worker.thread_signal.connect(self.handleMessages)
                            self.worker.data_signal.connect(self.numberDataHandler)
                            self.workers.append(self.worker)
                        
                        for w in self.workers:
                            w.start()
                            
                        # self.update_butt.setDisabled(True)
                        # self.waitGeneration()
                    
                    else:
                        self.service_field.setText('Wrong Service')
                        m = QTimer()
                        m.singleShot(1500,lambda: self.service_field.clear())

            def addRowConstructor(self,row_number):
                
                if row_number>=0:
                    
                    row_to_insert = row_number+1
                                    
                    new_object_name_number_field = f'number_field_{row_to_insert-1}'
                    new_object_name_code_field = f'code_field_{row_to_insert-1}'
                    new_object_name_number_copy = f'number_copy_btn_{row_to_insert-1}'
                    new_object_name_otp_copy = f'code_copy_but_{row_to_insert-1}'
                    new_object_name_country = f'country_name_{row_to_insert-1}'
                    new_object_name_service = f'service_name_{row_to_insert-1}'
                    new_object_name_code_status = f'code_status_{row_to_insert-1}'
                    new_object_name_cancel_button = f'cancel_number_but_{row_to_insert-1}'
                    new_single_container = f'single_container_{row_number}'
                    new_label_name = f'label_{row_number}'
                    new_label_2_name = f'label_2_{row_number}'
                    
                    # Construct the single container
                    self.single_container = QtWidgets.QGridLayout()
                    self.single_container.setHorizontalSpacing(12)
                    self.single_container.setVerticalSpacing(4)
                    self.single_container.setObjectName(new_single_container)
                    
                    # Construct the country service section
                    self.country_service_layout = QtWidgets.QHBoxLayout()
                    self.country_service_layout.setContentsMargins(10, -1, 10, -1)
                    self.country_service_layout.setObjectName("country_service_layout")
                    self.label_1 = QtWidgets.QLabel(self.gridLayoutWidget)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(0)
                    sizePolicy.setHeightForWidth(self.label_1.sizePolicy().hasHeightForWidth())
                    self.label_1.setSizePolicy(sizePolicy)
                    self.label_1.setMaximumSize(QtCore.QSize(80, 16777215))
                    self.label_1.setObjectName("label_1")
                    self.label_1.setText('Country:')
                    self.country_service_layout.addWidget(self.label_1)
                    
                    self.country_name_1 = QtWidgets.QLabel(self.gridLayoutWidget)
                    self.country_name_1.setMinimumSize(QtCore.QSize(210, 0))
                    self.country_name_1.setObjectName(new_object_name_country)
                    self.country_service_layout.addWidget(self.country_name_1)
                    
                    self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
                    self.label_2.setMaximumSize(QtCore.QSize(60, 16777215))
                    self.label_2.setObjectName(new_label_2_name)
                    self.label_2.setText('Service:')
                    self.country_service_layout.addWidget(self.label_2)
                    self.servic_name_1 = QtWidgets.QLabel(self.gridLayoutWidget)
                    self.servic_name_1.setObjectName(new_object_name_service)
                    self.country_service_layout.addWidget(self.servic_name_1)
                    self.single_container.addLayout(self.country_service_layout, 2, 0, 1, 1)
                    
                    # Construct the code section
                    self.code_layout = QtWidgets.QHBoxLayout()
                    self.code_layout.setSpacing(0)
                    self.code_layout.setObjectName("code_layout")
                    self.code_field_1 = QtWidgets.QLineEdit(self.gridLayoutWidget)
                    self.code_field_1.setEnabled(True)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(1)
                    sizePolicy.setHeightForWidth(self.code_field_1.sizePolicy().hasHeightForWidth())
                    self.code_field_1.setSizePolicy(sizePolicy)
                    self.code_field_1.setMinimumSize(QtCore.QSize(0, 30))
                    self.code_field_1.setMaximumSize(QtCore.QSize(2000, 16777215))
                    self.code_field_1.setStyleSheet("QLineEdit { text-align: center;border-top-right-radius:0px; border-bottom-right-radius:0px}\n"
                    "")
                    self.code_field_1.setText("")
                    self.code_field_1.setObjectName(new_object_name_code_field)
                    self.code_layout.addWidget(self.code_field_1)
                    self.code_copy_but1 = QtWidgets.QPushButton(self.gridLayoutWidget)
                    self.code_copy_but1.setMinimumSize(QtCore.QSize(130, 30))
                    self.code_copy_but1.setMaximumSize(QtCore.QSize(119, 16777215))
                    self.code_copy_but1.setStyleSheet("border-top-left-radius:0px; border-bottom-left-radius:0px")
                    self.code_copy_but1.setText("")
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap("copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.code_copy_but1.setIcon(icon)
                    self.code_copy_but1.setObjectName(new_object_name_otp_copy)
                    self.code_layout.addWidget(self.code_copy_but1)
                    self.single_container.addLayout(self.code_layout, 0, 2, 1, 1)
                    
                    # Construct the number section
                    self.number_layout = QtWidgets.QHBoxLayout()
                    self.number_layout.setSpacing(0)
                    self.number_layout.setObjectName("number_layout")
                    self.number_field_1 = QtWidgets.QLineEdit(self.gridLayoutWidget)
                    self.number_field_1.setEnabled(True)
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(0)
                    sizePolicy.setVerticalStretch(1)
                    sizePolicy.setHeightForWidth(self.number_field_1.sizePolicy().hasHeightForWidth())
                    self.number_field_1.setSizePolicy(sizePolicy)
                    self.number_field_1.setMinimumSize(QtCore.QSize(350, 30))
                    self.number_field_1.setMaximumSize(QtCore.QSize(200, 16777215))
                    self.number_field_1.setStyleSheet("QLineEdit { text-align: center;border-top-right-radius:0px; border-bottom-right-radius:0px}\n"
                    "")
                    self.number_field_1.setText("")
                    self.number_field_1.setObjectName(new_object_name_number_field)
                    self.number_layout.addWidget(self.number_field_1)
                    
                    self.number_copy_btn1 = QtWidgets.QPushButton(self.gridLayoutWidget)
                    self.number_copy_btn1.setMinimumSize(QtCore.QSize(80, 30))
                    self.number_copy_btn1.setMaximumSize(QtCore.QSize(150, 30))
                    self.number_copy_btn1.setStyleSheet("border-top-left-radius:0px; border-bottom-left-radius:0px")
                    self.number_copy_btn1.setText("")
                    self.number_copy_btn1.setIcon(icon)
                    self.number_copy_btn1.setObjectName(new_object_name_number_copy)
                    self.number_layout.addWidget(self.number_copy_btn1)
                    
                    self.single_container.addLayout(self.number_layout, 0, 0, 1, 1)
                    
                    # Construct the status and cancel section
                    self.status_cancel_layout = QtWidgets.QHBoxLayout()
                    self.status_cancel_layout.setContentsMargins(10, -1, 10, -1)
                    self.status_cancel_layout.setObjectName("status_cancel_layout")
                    self.code_status_1 = QtWidgets.QLabel(self.gridLayoutWidget)
                    self.code_status_1.setObjectName(new_object_name_code_status)
                    self.status_cancel_layout.addWidget(self.code_status_1)
                    self.cancel_number_but1 = QtWidgets.QPushButton(self.gridLayoutWidget)
                    self.cancel_number_but1.setMinimumSize(QtCore.QSize(40, 20))
                    self.cancel_number_but1.setMaximumSize(QtCore.QSize(30, 30))
                    self.cancel_number_but1.setText("")
                    icon1 = QtGui.QIcon()
                    icon1.addPixmap(QtGui.QPixmap("cancel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.cancel_number_but1.setIcon(icon1)
                    self.cancel_number_but1.setObjectName(new_object_name_cancel_button)
                    self.status_cancel_layout.addWidget(self.cancel_number_but1)
                    self.single_container.addLayout(self.status_cancel_layout, 2, 2, 1, 1)
                    self.contents_layout.addLayout(self.single_container, row_number, 0, 1, 1)
                    
                    
                    self.current_number_of_rows+=1
                    row_object ={
                        'row_number':row_number,
                        'number_field':self.number_field_1,
                        'number_copy':self.number_copy_btn1,
                        'code_field':self.code_field_1,
                        'code_copy':self.code_copy_but1,
                        'country':self.country_name_1,
                        'service':self.servic_name_1,
                        'status':self.code_status_1,
                        'cancel':self.cancel_number_but1,
                        'label':self.label_1,
                        'label2':self.label_2,
                        'container':self.single_container,
                        'number_id':'',
                        'time': '',
                        'had_code':'no',
                        'thread':''
                        
                    }
                    
                    if len(self.current_rows)==0:
                        add = 65
                    else:
                        add=80
                    # adjust the grid layout height
                    new_layout_widget_height = self.gridLayoutWidget.height() + add 
                    self.gridLayoutWidget.setGeometry(QtCore.QRect(11, 11, self.gridLayoutWidget.width(), new_layout_widget_height))
                    
                    
                    
                    if self.current_number_of_rows>6:
                        # adjust the centents widget of scroll area size
                        new_height_for_contents_widget = self.scrollAreaWidgetContents.height() + add
                        
                        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 929-20, new_height_for_contents_widget))
                        self.verScroll.setValue(new_height_for_contents_widget)
                        
                    
                    self.current_rows.append(row_object)
                    self.assignCopyButtons()
                    self.assignCancelButtons()
                    

                
            def assignNewNumber(self,number_id,number_index,row):
                
                self.newNumberThread = numberHandleThread(number_id,number_index,19)
                self.newNumberThread.status_signal.connect(self.handleNumberMessage)
                self.newNumberThread.time_update.connect(self.updateTimerFor)
                self.newNumberThread.run()
                
                row['handler'] = self.newNumberThread
                self.running_threads.append(self.newNumberThread)
                row['thread'] = self.newNumberThread
                
                
            def updateTimerFor(self,msg,index):
                
                if 'See' in msg:
                    time = msg
                else:
                    time = f'{msg} min'
                for row in self.current_rows:
                    if row['row_number'] == index:
                        self.target_rowT = row
                        break
                
                if msg == '0' :
                    
                    self.target_rowT['code_field'].setText(time)
                    self.target_rowT['thread'].stopUpdate()
                    self.target_rowT['code_field'].setText('Expired')
                    self.target_rowT['status'].setText('Number Expired')
                    
                else:
                    try:
                        self.target_rowT['code_field'].setText(time)
                    except RuntimeError:
                        pass
            def handleNumberMessage(self,msg,index):
                
                for row in self.current_rows:
                    if row['row_number'] == index:
                        self.target_rowS = row
                        break
                self.writeMessageTimer = QTimer()
                
            
                self.writeMessageTimer.singleShot(200,lambda: self.setMessage(msg,index))
                
                
            def setMessage(self,msg,index):
                
                try:
                    
                    self.target_rowS['status'].setText(msg)
                    
                    if 'Internet' in msg:
                        self.label_25.setText('You are Offline.')
                        self.update_butt.setDisabled(True)
                        self.handleMessages('Connection Lost')
                        self.body_widget.show()
                        self.con_timer.start(5000)
            
                    if 'STATUS_CANCEL' in msg:
                        
                        print(f'Number {self.target_rowS["number_field"].text()} was Cancelled')
                        self.target_rowS['code_field'].setText('Cancelled')
                        self.target_rowS['status'].setText('Number was Cancelled')
                        self.target_rowS['thread'].stopUpdate()
                        
                    if 'STATUS_OK' in msg:
                        
                        self.target_rowS['code_field'].clear()
                        self.target_rowS['status'].setText('Code Received')
                        self.newNumberThread.time_update.disconnect(self.updateTimerFor)
                        code = msg.split(':')[-1]
                        self.target_rowS['code_field'].setText(code)
                        self.target_rowS['had_code'] = 'yes'
                        self.target_rowS['thread'].stopUpdate()
                        
                        self.remove_this_row_timer = QTimer()
                        self.remove_this_row_timer.singleShot(15000,lambda: self.cancel_number(self.target_rowS['number_id']))
                        
                except RuntimeError:
                    pass
                
            def numberDataHandler(self,number_data):
                
                
                if 'Internet' in number_data:
                    self.handleMessages('No Internet')
                    
                elif 'NO_BALANCE' in number_data[0]:
                    self.handleMessages('No Enough Balance')
                else:
                    try:
                        last_row = self.current_rows[-1]
                    except IndexError:
                        last_row = {'row_number':0}
                        
                    self.addRowConstructor(last_row['row_number']+1)
                    
                    # Extract Generated Number Data
                    number = number_data[0].split(':')[2]
                    number_id = number_data[0].split(':')[1]
                    country_name = number_data[1]
                    service_name = number_data[2]
                    current_time = f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}'
                    
                    # Edit number for country code
                    for country_object in self.country_codes:
                        if country_name == country_object['name']:
                            self.dial_code = country_object['dial_code']
                    
                    generated_row = self.current_rows[-1]
                    # Assign Number Data to newly generated row
                    number = f'+{number}'.replace(self.dial_code,'')
                    generated_row['number_field'].setText(number)
                    generated_row['country'].setText(country_name+f' {self.dial_code}')
                    generated_row['service'].setText(service_name)
                    generated_row['number_id'] = number_id
                    generated_row['time'] = current_time
                    
                    # Assign a Thread to Wait for the sent code
                    self.assignNewNumber(number_id,generated_row['row_number'],generated_row)
                    # Update Balance
                    self.number_generated = True
                    self.getbalance()
                
                
            def numberGeneratedMsg(self):
                
                self.cost = round(self.prevoius_balance - self.current_balance,2)
                text = f'Number {self.current_rows[-1]["number_field"].text()} Generated for {self.cost} $'
                self.number_notify_text.setText(text)
                self.number_notification.show()
                self.release = QTimer()
                self.release.singleShot(5000,lambda: self.number_notification.hide())
        
                    
            def assignCopyButtons(self):
                for rowobject in self.current_rows:
                    try:
                        rowobject['number_copy'].clicked.disconnect(self.copyTextHandle)
                        rowobject['code_copy'].clicked.disconnect(self.copyTextHandle)
                    except:
                        pass
                
                for rowobject in self.current_rows:
                    rowobject['number_copy'].clicked.connect(self.copyTextHandle)
                    rowobject['code_copy'].clicked.connect(self.copyTextHandle)
                    

            def copyTextHandle(self):
                clicked_button = self.gridLayoutWidget.sender()
                button_row = clicked_button.objectName().split('_')[-1]
                for index,item in enumerate(self.current_rows):
                    if item['row_number']==int(button_row):
                        text_to_copy_index=index
                        
                if 'number_copy' in clicked_button.objectName():
                    field_to_copy = self.current_rows[text_to_copy_index]['number_field']
                elif 'code_copy' in clicked_button.objectName():
                    field_to_copy = self.current_rows[text_to_copy_index]['code_field']
                text = field_to_copy.text()
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                                    
            def removeRowHandle(self,row_index):
                
                self.cancel_confirm.hide()
                
                for index,item in enumerate(self.current_rows):
                    if item['row_number']==row_index:
                        row_to_remove = item
                        index_in_list = index
                        break

                cont_to_remove = row_to_remove['container']
            
                for widget in row_to_remove.values():
                    try:
                        cont_to_remove.removeWidget(widget)
                        widget.deleteLater()
                    except:
                        pass
                
                
                row_at_pos = self.contents_layout.itemAtPosition(row_index,0)
                self.contents_layout.removeItem(row_at_pos)
                

                if len(self.current_rows)==1:
                    remove = 81
                else:
                    remove = 80
                # adjust the grid layout heigh
                new_layout_widget_height = self.gridLayoutWidget.height() - remove 
                self.gridLayoutWidget.setGeometry(QtCore.QRect(11, 11, self.gridLayoutWidget.width(), new_layout_widget_height))
                self.current_number_of_rows-=1
                self.current_rows.pop(index_in_list)
                print(f'removed item {index_in_list} from rows list')
                
                if self.current_number_of_rows>6:
                    # adjust the centents widget of scroll area size
                    new_height_for_contents_widget = self.scrollAreaWidgetContents.height() - remove
                    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, self.scrollAreaWidgetContents.width(), new_height_for_contents_widget))
            
                if self.current_number_of_rows<7:
                    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 929,self.scrollArea.height()))
            
                if not self.no_connection:
                    self.number_generated = False
                    self.getbalance()
                    
                self.service_field.clearFocus()
                self.secret_field_1.clearFocus()

                
            def cancel_number(self,number_id):
                
                for row_number in self.current_rows:
                    if row_number['number_id'] == number_id:
                        self.target_number_to_cancel = row_number
                        
                self.target_number_to_cancel['thread'].stopUpdate()
                self.cancelThread = setStatusThread(number_id)
                self.cancelThread.response_singal.connect(self.cancelResponse)
                self.handleMessages('Canceling Number')
                self.cancelThread.start()

            
            def cancelResponse(self,res):
                
                try:
                    if 'ACCESS_CANCEL' in res:
                        self.handleMessages('Number Canceled')
                        self.removeRowHandle(self.row_index)
                    else:
                        try:
                            if self.target_number_to_cancel['status'].text() in ['Number was Cancelled','Number Expired']:
                                self.removeRowHandle(self.target_number_to_cancel['row_number'])
                            self.handleMessages('You Must wait 2 minutes')
                        except RuntimeError:
                            pass
                except UnboundLocalError:
                    pass
                    
            def cleanClose(self):
                
                print('Clean Close Triggered')
                js = open('config.json','r') 
                data = json.load(js)
                data['lastservice'] = self.service_field.text()
                data['secret'] = self.secret_field_1.text()
                data['no_times'] = self.timesNumber.text()
                
                m = open('config.json','w')
                json.dump(data,m)
                
                # Save numbers present on closing the window
                self.numbers_on_close =[]
                for row in self.current_rows:
                    number = row['number_field'].text()
                    country = row['country'].text()
                    service = row['service'].text()
                    number_time = row['time']
                    number_had_code = row['had_code']
                    number_code = row['code_field'].text()
                    number_id = row['number_id']
                    
                    row_instance = {
                        'number':number,
                        'country':country,
                        'service':service,
                        'number_time':number_time,
                        'number_had_code':number_had_code,
                        'number_code':number_code,
                        'number_id':number_id
                    }
                    
                    self.numbers_on_close.append(row_instance)
                    
                    
                # Save last view to json file
                with open('current_numbers.json','w') as c:
                    json.dump(self.numbers_on_close,c)
                    
                m = myview()
                
                    
                for running_thread in self.running_threads:
                    running_thread.stopUpdate()
                    
                try:
                    self.worker.stop_generate_signal.emit()
                except AttributeError:
                    pass
                
                otps_window.finished.disconnect(self.cleanClose)
                self.target_countries.stopSearch()
                self.listWidget_2.clear()
                self.label_17.clear()
                
            def readLastView(self):
                with open('current_numbers.json','r') as c:
                    n=json.load(c)
                    
                self.saved_numbers = n
                
                
                self.current_status_thread = getCurrentActivationThread()
                self.current_status_thread.status_signal.connect(self.handleCurrentStatus)
                self.current_status_thread.start()
                
                    
            def handleCurrentStatus(self,waiting_list,received_list):
                actual_waiting_numbers = []
                actual_received_code_numbers = []
                # Check for waiting numbers
                found = False
                for row_object in self.saved_numbers:
                    for waiting_number in waiting_list:
                        if int(row_object['number_id']) == waiting_number['numberid']:
                            actual_waiting_numbers.append(waiting_number)
                            found = True
                            break
                    # Check for received code numbers
                    if not found:
                        for received_code_number in received_list:
                            if int(row_object['number_id']) == received_code_number['numberid']:
                                actual_received_code_numbers.append(received_code_number)

                n=1
                self.created_thread_objectss = []
                
                for wait_number in waiting_list:
                    # print(wait_number)
                    # print(actual_waiting_numbers)
                    if wait_number in actual_waiting_numbers:
                        pass
                    else:
                        self.addRowConstructor(n)
                        created_row = self.current_rows[-1]
                        
                        # Assign values to created row from server
                        created_row['number_field'].setText(wait_number['number'])
                        created_row['country'].setText('Unknown')
                        created_row['service'].setText('Unknown')
                        created_row['number_id'] = wait_number['numberid']
                        created_row['time'] = 'unknown'
                        
                        self.newNumberThread = numberHandleThread(created_row['number_id'],created_row['row_number'],'unknown')
                        self.newNumberThread.status_signal.connect(self.handleNumberMessage)
                        self.newNumberThread.time_update.connect(self.updateTimerFor)
                        self.created_thread_objectss.append(self.newNumberThread)
                        created_row['thread'] = self.newNumberThread
                        
                        n+=1
                        
                for number in actual_waiting_numbers:
                    
                    self.addRowConstructor(n)
                    
                    created_row = self.current_rows[-1]
                    
                    for index,saved_number in enumerate(self.saved_numbers):
                        if number['numberid'] == int(saved_number['number_id']):
                            number_index_in_saved_list = index
                            break
                        
                    saved_row = self.saved_numbers[number_index_in_saved_list]
                    current_time = f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}'
                    
                    # Assign values to created row from saved rows
                    created_row['number_field'].setText(saved_row['number'])
                    created_row['country'].setText(saved_row['country'])
                    created_row['service'].setText(saved_row['service'])
                    created_row['number_id'] = number['numberid']
                    created_row['time'] = saved_row['number_time']
                    
                    
                    # Check for availablitiy
                    current_time = f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}'
                    current_hour = int(current_time.split(':')[0])
                    current_minute = int(current_time.split(':')[1])
                    

                    availablity= False
                    saved_time = saved_row['number_time']
                    if saved_time == 'unknown':
                        rem_time = 'unknown'
                        availablity = True
                        
                    else:
                        
                        saved_hour = int(saved_time.split(':')[0])
                        saved_minute = int(saved_time.split(':')[1])
                        if current_hour-saved_hour>1:
                            status = 'Number Expired'
                        elif current_hour-saved_hour == 1:
                            remaining_time = current_minute-saved_minute+60
                            if remaining_time>20:
                                status = 'Number Expired'
                            elif remaining_time<=20:
                                availablity = True
                                rem_time = 19-remaining_time
                        elif current_hour-saved_hour ==0:
                            remaining_time = current_minute-saved_minute
                            if remaining_time>20:
                                status = 'Number Expired'
                            elif remaining_time<=20:
                                availablity = True
                                rem_time = 19-remaining_time
                        elif saved_hour==23 and current_hour==1:
                            remaining_time = current_minute-saved_minute+60
                            if remaining_time>20:
                                status = 'Number Expired'
                            elif remaining_time<=20:
                                availablity = True
                                rem_time = 19-remaining_time
                        else:
                            status = 'Number Expired'
                        
                    if availablity:
                        self.newNumberThread = numberHandleThread(number['numberid'],created_row['row_number'],rem_time)
                        self.newNumberThread.status_signal.connect(self.handleNumberMessage)
                        self.newNumberThread.time_update.connect(self.updateTimerFor)
                        self.created_thread_objectss.append(self.newNumberThread)
                        created_row['thread'] = self.newNumberThread
                    else:
                        created_row['code_field'].setText(status)
                
                    n+=1
                    
                    
                for number in actual_received_code_numbers:
                    
                    self.addRowConstructor(n)
                    
                    for index,saved_number in enumerate(self.saved_numbers):
                        if number['numberid'] == int(saved_number['number_id']):
                            number_index_in_saved_list = index
                            break
                        
                    created_row = self.current_rows[-1]
                    saved_row = self.saved_numbers[number_index_in_saved_list]
                    current_time = f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}'
                    
                    # Assign values to created row from saved rows
                    created_row['number_field'].setText(saved_row['number'])
                    created_row['country'].setText(saved_row['country'])
                    created_row['service'].setText(saved_row['service'])
                    created_row['number_id'] = number['numberid']
                    created_row['time'] = current_time
                    
                    self.newNumberThread = numberHandleThread(number['numberid'],created_row['row_number'],20)
                    self.newNumberThread.status_signal.connect(self.handleNumberMessage)
                    self.newNumberThread.time_update.connect(self.updateTimerFor) 
                    self.created_thread_objectss.append(self.newNumberThread)
                    created_row['thread'] = self.newNumberThread
                    
                    n+=1
                
                
                for thread_object in self.created_thread_objectss:
                        thread_object.run()
                        self.running_threads.append(thread_object)
                        
                self.body_widget.hide()
                self.setWaitStatus()
                    
            def setWaitStatus(self):
                for row in self.current_rows:
                    row['status'].setText('Waiting Code...')
                    
            
            def checkForConnectionBack(self):
                self.checkConnection()
                if self.no_connection:
                    pass
                else:
                    
                    # Refresh the Window
                    self.con_timer.stop()
                    self.close_button.click()
                    n.otpsWindowCLosed()
                    
                
            # OTP Part
            def installOTP(self):
                self.secret_field_1.textChanged.connect(self.senseTheChange)
                self.copy_button_1.clicked.connect(self.copyTextHandle)
            
            def copyTextHandle(self):
               
                self.generat_otp_for(self.secret_field_1)
                text = self.otp_field_1.text()
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                
            def senseTheChange(self,event):
                
                self.changed_field = self.gridLayoutWidget.sender()
                self.generat_otp_for(self.changed_field)
                
            def generat_otp_for(self,changed_field):
                
                secret = changed_field.text()    
               
                if len(secret)==64:
                    try:
                        totp = pyotp.TOTP(secret.replace(' ',''))
                        otp = totp.now()        
                        self.otp_field_1.setText(otp)
                    except:
                        self.otp_field_1.setText("Invalid")
                else:
                    self.otp_field_1.setText("Invalid")
            
        x = updatedOTPsWindow()
        x.normalView(otps_window)
        otps_window.exec()
        
    def otpsWindowCLosed(self):
        print('window Refresh Trigger')
        self.qtimer = QTimer()
        self.qtimer.singleShot(1000,lambda: self.OTPsWindow())
        
if __name__=='__main__':
    import sys
    app = QApplication(sys.argv)
    wind = QDialog()
    otps_window = QDialog()
    wind.setWindowIcon(QIcon('icon.svg'))
    otps_window.setWindowIcon(QIcon('icon.svg'))
    n = myview()
    n.startview(window=wind)
    wind.show()
    app.exec()