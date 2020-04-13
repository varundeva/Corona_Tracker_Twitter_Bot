import tweepy
import requests
import time
from datetime import datetime
import logging
import re
import credentials #credentials.py file contains all 4 tokens and secrets


auth = tweepy.OAuthHandler(credentials.consumer_key, credentials.consumer_secret)
auth.set_access_token(credentials.access_token, credentials.access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)  #Auth Responce Stored in Variable Api. 

logging.basicConfig(filename="global_error.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

#Tweet Global Statistics
def globalDataTweet():
    #API End Point
    url = "https://covid19-server.chrismichael.now.sh/api/v1/AllReports"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        cases = data['reports'][0]['cases']
        deaths = data['reports'][0]['deaths']
        recovered = data['reports'][0]['recovered']
        cases = format (cases, ',d')
        deaths =format (deaths, ',d')
        recovered = format (recovered, ',d')
        sendTweet(cases,deaths,recovered)
        
    else:
        print("API Error - " + str(datetime.now()))
        logger.error("API Error") 

# Function to Send Tweets /  This function called in globalDataTweet() function
def sendTweet(cases,deaths,recovered):
    tweetText = "🦠COVID-19 CORONAVIRUS🦠 PANDEMIC \n🌎Global Data🌐 \n\n😟Total Cases : "+str(cases)+"\n😀Total Recoverd : "+str(recovered)+"\n😔Total Deaths : "+str(deaths)+"\n#Corona #Covid19 #Coronavirus #Follow #CoronaUpdate"
    if api.update_status(tweetText):
        print('tweeted')
    else:
        print('error in tweepy')

#Do Tweet Every Hour 
while True:
    try:
        globalDataTweet()
    except tweepy.TweepError as error:
        print(error)
    time.sleep(3600)
