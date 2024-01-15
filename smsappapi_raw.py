import requests
import random

api_key = '11ad6487483867694afe8c943af189da'
lang = 'en'
country = 'russia'
service = 'amazon'
operator = 'any'
max_price = '0.08'

def getBalance(): 
    msg = 'Getting Balance'
    print(msg)
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getBalance&lang={lang}'
    reqo = requests.get(url)
    try:
        return reqo.json()
    except:
        return f'Error on Get Balance function with response {reqo.text}'

def getServiceCode(service=''):
   
    s = open('services.txt','r')
    cont = s.read()
    sepa = cont.split('\n')
    filtered_sepa = [item for item in sepa if item!='']
    for index,servicee in enumerate(filtered_sepa):
        if service.lower() == servicee.lower():
            our_id = filtered_sepa[index-1]
            break
        else:
            our_id = 'None'
            servicee = service
    return our_id,servicee

def getCountryCode(country=''):
    
    try:
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCountryAndOperators&lang={lang}'
        reqo = requests.get(url)
        countries = reqo.json()
    except Exception as e:
        print(e)
    
    for country_name in countries:
        if country.lower() == country_name['name'].lower():
            our_id = country_name['id']
            break
        else:
            our_id = 'None'
    return our_id,country_name['name']
    
def getCountryAndOperators():
    msg = 'Getting Current Countries and Operators'
    print(msg)
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCountryAndOperators&lang={lang}'
    reqo = requests.get(url)
    try:
        return reqo.json()
    except:
        return f'Error on Countries function with response {reqo.text}'

def getServicesAndCost(country=country,operator=operator,service=service):
    service_id = getServiceCode(service)[0]
    country_id = getCountryCode(country)[0]
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getServicesAndCost&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
    reqo = requests.get(url)
    try:
        return reqo.json(),country,service
    except:
        return reqo.text,country,service

def getServicesAndCostWithStatistics(service=service):
    
    # Pick a random Country to get stats for
    countries = getCountryAndOperators()
    list_of_countries =[]
    for count in countries:
        list_of_countries.append(count['name'])
    rand = random.randint(0,len(list_of_countries)-1)
    random_country = list_of_countries[rand]
    
    country_id = getCountryCode(random_country)[0]
    service_id = getServiceCode(service)[0]
    
    msg = 'Getting Current Status and Available Numbers'
    print(msg)
    
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getServicesAndCostWithStatistics&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
    reqo = requests.get(url)
    try:
        return reqo.json(),random_country
    except Exception as e:
        return reqo.text,random_country,service

def getNumber(service=service):
    msg = 'Getting Service Code'
    print(msg)
    service_id = getServiceCode(service)[0]
    if service_id=='None':
        return f'Wrong Service'
    # Pick up random country for number with set cost
    current_stats = getServicesAndCostWithStatistics(service=service)
    msg = 'Picking random number'
    print(msg)
    target_price_countries =[]
    for avcountry in current_stats[0][0]['cheap_prices_countries']:
        if float(avcountry['price']) <= float(max_price):
            target_price_countries.append(avcountry['country_name'])
        else:
            break
    while True:
        rand = random.randint(0,len(target_price_countries)-1)
        random_country = target_price_countries[rand]
        country_id = getCountryCode(random_country)[0]
        url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getNumber&country={country_id}&operator={operator}&service={service_id}&lang={lang}'
        reqo = requests.get(url)
        if reqo.text in ['NO_NUMBERS','BAD_ACTION']:
            print('Trying again')
            continue
        else:
            return reqo.text,random_country,service
            
    

def setStatus(ID,STATUS):
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=setStatus&id={ID}&status={STATUS}&lang={lang}'
    reqo = requests.get(url)
    return reqo.text

def getStatus(number_id):
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getStatus&id={number_id}&lang={lang}'
    reqo = requests.get(url)
    return reqo.text

def getCurrentActivationsList(status,limit):
    url = f'https://sms-activation-service.com/stubs/handler_api?api_key={api_key}&action=getCurrentActivationsList&status={status}&limit={limit}&order=id&orderBy=ASC&lang={lang}'
    reqo = requests.get(url)
    return reqo.json()
