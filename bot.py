import tweepy
import requests
import time
from datetime import datetime
import logging
import re
import credentials #credentials.py file contains all 4 tokens and secrets

file_name = 'last_seen_id.txt'

auth = tweepy.OAuthHandler(credentials.consumer_key, credentials.consumer_secret)
auth.set_access_token(credentials.access_token, credentials.access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)  #Auth Responce Stored in Variable Api. 

logging.basicConfig(filename="country_error.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)


def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def sendCountryReply(cases,deaths,recovered,id,name,country_name):
    tweetText = " Hey "+name+"\n🦠COVID-19 CORONAVIRUS🦠\n🌎Data of Country - "+country_name.capitalize()+"🌐 \n\n😟Total Cases : "+str(cases)+"\n😀Total Recoverd : "+str(recovered)+"\n😔Total Deaths : "+str(deaths)+"\n#Corona #Covid19 #Coronavirus #Follow #CoronaUpdate"
    if api.update_status('@'+ name + tweetText,id):
        store_last_seen_id(id, file_name)
        print('Reply Sent')
    else:
        text = ' Something Wrong..\n Please Try Again After Sometime \n\n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
        api.update_status('@'+ name +text ,id)
        store_last_seen_id(id, file_name)
        print('Failed to send Reply')

def sendStateReply(activeCases,confimedCases,deaths,recovered,stateName,lut,id,name):
    tweetText =" Hey "+name+"!\n🦠COVID-19 #CORONAVIRUS PANDEMIC 🦠\n📍"+stateName.capitalize()+" State📍\n😟active - "+activeCases+"\n😢confirmed - "+confimedCases+"\n😔deaths - "+deaths+"\n😃recovered - "+recovered+"\nStay Home | Stay Safe\n⌛Last Update - "+lut+"\n#CornaVirus #Covid19 #Follow #Updates"
    if api.update_status('@'+ name + tweetText,id):
        store_last_seen_id(id, file_name)
        print('Reply Sent to '+name)
    else:
        text = ' Something Wrong..\n Please Try Again After Sometime \n\n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
        api.update_status('@'+ name +text ,id)
        store_last_seen_id(id, file_name)    
        
def statePost(stateCode,id,name):
    #STATE API End Point
    url = "https://api.covid19india.org/data.json"
    res = requests.get(url)
    stateName=activeCases=confimedCases=deaths=recovered=lut =""
    isDataAvailable=""
    if res.status_code == 200:
        data = res.json()
        for state in data['statewise']:
            if stateCode.upper() == state['statecode'].upper():
                print("State Code Valid")
                activeCases = format(int(state['active']),',d')
                confimedCases = format(int(state['confirmed']),',d')
                deaths = format(int(state['deaths']),',d')
                recovered = format(int(state['recovered']),',d')
                stateName = state['state']
                lut = state['lastupdatedtime']
                isDataAvailable = True
                break
            # else:
            #     print("Invalid State Code")
            #     text=' Something Wrong...\nPlease Try Again After Sometime.\nPlease Use Correct State Code (2Letters)\n\nMention - @Covid19Stat_bot then #state [State Code] \n Ex- @Covid19Stat_bot #state DL \n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
            #     api.update_status('@'+ name + text,id)
            #     store_last_seen_id(id, file_name) 
        if isDataAvailable == True:
            print("Calling sendStateReply()")
            sendStateReply(activeCases,confimedCases,deaths,recovered,stateName,lut,id,name)
        else:
            print("Invalid State Code")
            text=' Something Wrong...\nPlease Try Again After Sometime.\nPlease Use Correct State Code (2Letters)\n\nMention - @Covid19Stat_bot then #state [State Code] \n Ex- @Covid19Stat_bot #state DL \n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
            api.update_status('@'+ name + text,id)
            store_last_seen_id(id, file_name) 
    else:
        text=' Something Wrong..\nPlease Try again Later\nPlease Follow Correct Method and Try Again Later\n\nMention @Covid19Stat_bot then #state [State Code] \n Ex- @Covid19Stat_bot #state DL \n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
        api.update_status('@'+ name + text,id)
        store_last_seen_id(id, file_name)
        print("State API Error - " + str(datetime.now()))
        logger.error("State API Error")
    


def countryPost(country,id,name):
    #COUNTRY API End Point
    url = "https://covid19-server.chrismichael.now.sh/api/v1/ReportsByCountries/"
    res = requests.get(url+country)
    if res.status_code == 200:
        data = res.json()
        cases = data['report']['cases']
        deaths = data['report']['deaths']
        recovered = data['report']['recovered']
        country_name = data['report']['country']
        cases = format (cases, ',d')
        deaths =format (deaths, ',d')
        recovered = format (recovered, ',d')
        sendCountryReply(cases,deaths,recovered,id,name,country_name)
    else:
        text=' Something Wrong..\n Please Follow Correct Method Mention @Covid19Stat_bot then #country [Country Name (use - between 2 words] \n Ex- @Covid19Stat_bot #country us \n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
        api.update_status('@'+ name + text,id)
        store_last_seen_id(id, file_name)
        print("API Error - " + str(datetime.now()))
        logger.error("API Error")
        

def MentionWatch():
    last_seen_id = retrieve_last_seen_id(file_name)
    mentions = api.mentions_timeline(last_seen_id)
    for mention in reversed(mentions):
        if mention.user.id == 849074973301977088 :
            print("self mention found")
            store_last_seen_id(mention.id, file_name)
            break
        print(str(mention.id)+ ' - ' +mention.user.screen_name)
        words = mention.text.lower().split()
        if '#country' in words:
                print('found #country', flush=True)
                country_name =""
                regx = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
                for i in range(len(words)):
                    word =words[i]
                    if(regx.search(word)==None):
                        country_name = word
                        break
                print(country_name)
                time.sleep(5)
                countryPost(country_name,mention.id,mention.user.screen_name)
                time.sleep(15)
        elif '#state' in words:
                print('found #state', flush=True)
                state_code =""
                regx = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
                for i in range(len(words)):
                    word =words[i]
                    if(regx.search(word)==None):
                        state_code = word
                        break
                print(state_code)
                time.sleep(5)
                statePost(state_code,mention.id,mention.user.screen_name)
                time.sleep(15)
        else:
            text=' Something Wrong..\n Please Follow Correct Method Mention @Covid19Stat_bot then #country [Country Name (use - between 2 words] \n Ex- @Covid19Stat_bot #country us \n Follow Us \n #Corona #Covid19Updates #CoronaUpdate'
            api.update_status('@'+ mention.user.screen_name + text,mention.id)
            store_last_seen_id(mention.id, file_name)
            print("#country not available")


while True:
    try:
        MentionWatch()
    except tweepy.TweepError as error:
        print(error)
    time.sleep(30)
