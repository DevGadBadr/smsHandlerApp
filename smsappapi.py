import requests
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
from cryptography.fernet import Fernet
import time


# Default inputs
lang = 'en'
country = 'russia'
service = 'amazon'
operator = 'any'

# Read Parameters from json
b = open('config.json','r')
n = json.load(b)
api_key = n['api-key']

# Read max cost
key = n['data3']
enc_number = n['data4']
cipher_suite = Fernet(key)
decrypted_number = cipher_suite.decrypt(enc_number).decode('utf-8')
max_price = decrypted_number


class API_Handler(QObject):
    
    signal_sender = pyqtSignal(str)
    app_online = True
    countries_signal = pyqtSignal(list)
    writing_now = False
    
    def messages_test(self):
        while True:
                
            msg = 'Getting Balance'
            self.signal_sender.emit(msg)
            time.sleep(1)
            msg = 'Getting Current Status and Available Numbers'
            self.signal_sender.emit(msg)
            time.sleep(1)
             
    def getBalance(self): 
        msg = 'Getting Balance'
        self.signal_sender.emit(msg)
        print(msg)
        
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getBalance&lang={lang}'
        try:
            reqo = requests.get(url)
        except ConnectionError:
            return 'No Internet'
        
        try:
            return reqo.json()
        except:
            return f'Error on Get Balance function with response {reqo.text}'

    def getServiceCode(self,service=''):
    
     
        with open('services.json','r',encoding='utf-8') as j:
             s = json.load(j)
             
        if service in s:
            return s[service],service
        else:
            return 'wrong service'

    def getCountryCode(self,country=''):
        
        try:
            url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCountryAndOperators&lang={lang}'
            reqo = requests.get(url)
            countries = reqo.json()
            suc = True
        except Exception as e:
            suc = False
            print(e)
        
        if suc:
            for country_name in countries:
                if country.lower() == country_name['name'].lower():
                    our_id = country_name['id']
                    break
                else:
                    our_id = 'None'
            return our_id,country_name['name']
        
    def getCountryAndOperators(self):
        msg = 'Getting Current Countries and Operators'
        self.signal_sender.emit(msg)
        print(msg)
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCountryAndOperators&lang={lang}'
        reqo = requests.get(url)
        try:
            return reqo.json()
        except:
            return f'Error on Countries function with response {reqo.text}'

    def getServicesAndCost(self,country=country,operator=operator,service=service):
        service_id = self.getServiceCode(service)[0]
        country_id = self.getCountryCode(country)[0]
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getServicesAndCost&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
        reqo = requests.get(url)
        try:
            return reqo.json(),country,service
        except:
            return reqo.text,country,service

    def getServicesAndCostWithStatistics(self,service=service):
        
        # Pick a random Country to get stats for
        countries = self.getCountryAndOperators()
        list_of_countries =[]
        for count in countries:
            list_of_countries.append(count['name'])
        rand = random.randint(0,len(list_of_countries)-1)
        random_country = list_of_countries[rand]
        
        while True:
            country_id = self.getCountryCode(random_country)[0]
            service_id = self.getServiceCode(service)[0]
            
            msg = 'Getting Current Status and Available Numbers'
            self.signal_sender.emit(msg)
            print(msg)
            
            url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getServicesAndCostWithStatistics&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
            reqo = requests.get(url)
            try:
                return reqo.json(),random_country
            except Exception as e:
                if reqo.text=='ERROR_API' and random_country!='Russia':
                    random_country = 'Russia'
                    continue
                else:
                    return 'No avaialable Numbers for this service'
           
    def searchTargetNumbers(self,service):
       
        # Read last index to continue from in the countries list
        with open('config.json','r') as g:
            f = json.load(g)
            n=f['count']+1
            
        # While app running keep looking for countries and prices
        while self.app_online:
            m = self.getCountryAndOperators()
            countries=[]
            self.target=[]
            flist=[]
            for item in m:
                country_name = item['name']
                countries.append(country_name)
            self.checkCurrentCountries()
            print(self.target)
            if len(self.target)==0:
                n=0
            n=0
            for country in countries[n:]:
                if self.app_online:
                    f = self.getServicesAndCost(country,'any',service)
                    print(f)
                    flist.append(f)
                    if f[0][0]['price'] <=float(max_price) and f[1]!="Russia":
                        if f'{f[1]}  {f[0][0]["price"]}$' not in self.clean:
                            self.target.append(f)
                            print(self.target)
                            self.writeCountries()
                            self.countries_signal.emit(self.target)
                    elif f[0][0]['price'] >float(max_price) and f[1]!="Russia":
                        if f in self.target or f'{f[1]}  {f[0][0]["price"]}$' in self.clean:
                            
                            try:
                                self.target.remove(f)
                            except ValueError:
                                print(self.target)
                                cell = ([{'price':f[0][0]['price']}],f[1],'Amazon')
                                self.target.remove(cell)
                                
                            print(self.target)
                            self.writeCountries()
                            self.countries_signal.emit(self.target)
                            
                    print(f'{countries.index(country)}/{len(countries)}')
                    index = countries.index(country)
                else:
                    break
            
            n=0         
            
            
        if not self.app_online:
            j = open('config.json','r') 
            m = json.load(j)
            m['count'] = index
            f = open('config.json','w')
            json.dump(m,f)
            
     
    def checkCurrentCountries(self):
        with open('target_countries.txt','r') as g:
            n = g.readlines()
            self.clean=[]
            for i in n:
                f = i.replace('\n','')
                self.clean.append(f)
        g.close
        for country in list(set(self.clean)):
            country_tuple = ([{'price':float(country.split(' ')[-1].replace('$',''))}],country.split(' ')[0],'Amazon')
            self.target.append(country_tuple)
                    
    def writeCountries(self):
        
        with open('target_countries.txt','w') as g:
            self.writing_now = True
            for item in self.target:
                g.write(f'{item[1]}  {item[0][0]["price"]}$'+'\n')
        g.close
        self.writing_now = False
        
    def getNumber(self,service=service):
        msg = 'Getting Service Code'
        print(msg)
        self.signal_sender.emit(msg)
        service_id = self.getServiceCode(service)[0]
        if service_id=='None':
            print('Wrong Service')
            return f'Wrong Service'
        # Pick up random country for number with set cost
        self.Continue_generate_number = True     
        msg = 'Picking a random Country'
        print(msg)
        self.signal_sender.emit(msg)
        while True:
            if self.writing_now:
                print('Detected trying read while writing')
            else:
                with open('target_countries.txt','r') as g:
                    n = g.readlines()
                    clean=[]
                    for i in n:
                        f = i.replace('\n','')
                        f = f.split(' ')[0]
                        clean.append(f)
                g.close
                break
        target_price_countries =list(set(clean))
        random.shuffle(target_price_countries)
        msg = 'Confirming Price'
        print(msg)
        self.signal_sender.emit(msg)
        got_country = False
       
        trial = 0
        print(target_price_countries)
        print(len(target_price_countries))
        while self.Continue_generate_number:
            # shuffle and start taking
            for c in target_price_countries:
                country = c
                current_stat = self.getServicesAndCost(country,'any',service)
                if current_stat[0][0]['price'] <= float(max_price):
                    got_country = True
                    break
                else:
                    print(f'Country {country} does not meet target Trying again')
                    continue
            if got_country:
                pass
            else:
                msg = 'No Countries Available with this Price'
                self.signal_sender.emit(msg)
                return None

            msg = f'Trying for {country}'
            print(msg)
            self.signal_sender.emit(msg)
            country_id = self.getCountryCode(country)[0]
            
            url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getNumber&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
            reqo = requests.get(url)
            
            if reqo.text in ['NO_NUMBERS','BAD_ACTION']:
                print(reqo.text)
                msg = 'Finding Number with requirements'
                self.signal_sender.emit(msg)
                if self.Continue_generate_number and trial<len(target_price_countries):
                    trial+=1
                    print(f'Trial {trial}')
                    continue
                else:
                    print(len(target_price_countries))
                    print('Searching Cancelled or finished')
                    return 'Searching Cancelled or finished'
            else:
                print(reqo.text)
                msg = 'Number Generated'
                self.signal_sender.emit(msg)
                return reqo.text,country,service
                   
    def setStatus(self,ID,STATUS):
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=setStatus&id={ID}&status={STATUS}&lang={lang}'
        reqo = requests.get(url)
        return reqo.text

    def getStatus(self,number_id):
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getStatus&id={number_id}&lang={lang}'
        reqo = requests.get(url)
        return reqo.text

    def getCurrentActivationsList(self,status,limit):
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCurrentActivationsList&status={status}&limit={limit}&order=date&orderBy=DESC&lang={lang}'
        reqo = requests.get(url)
        return reqo.json()
    
    def stopNumberGenerating(self):
        print('Generating Stopped')
        self.Continue_generate_number = False
    
    def stopSearchingCountries(self):
        self.app_online = False

x = API_Handler()