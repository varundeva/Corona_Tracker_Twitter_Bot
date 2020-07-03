import tweepy
import requests
import time
import logging
import re
import json
from datetime import datetime, timezone
import schedule
import credentials #credentials.py file contains all 4 tokens and secrets


auth = tweepy.OAuthHandler(credentials.consumer_key, credentials.consumer_secret)
auth.set_access_token(credentials.access_token, credentials.access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)  #Auth Responce Stored in Variable Api. 

logging.basicConfig(filename="KADist_error.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

#Tweet Global Statistics
def DistrictDataTweet():
    #API End Point
    url = "https://api.covid19india.org/v3/data.json"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        for dist in data['KA']['districts'].items():
            distName = dist[0]

            if 'confirmed' in dist[1]['total']:
                confirmed = format(dist[1]['total']['confirmed'],',')
            else:
                confirmed = '0'

            if 'recovered' in dist[1]['total']:
                recovered = format(dist[1]['total']['recovered'],',')
            else:
                recovered = '0'

            if 'deceased' in dist[1]['total']:
                deceased = format(dist[1]['total']['deceased'],',')
            else:
                deceased = '0'
            
            if 'tested' in dist[1]['total']:
                tested = format(dist[1]['total']['tested'],',')
            else:
                tested = '0'

            sendTweet(distName,confirmed,recovered,deceased,tested)
            time.sleep(15)
        
    else:
        print("API Error - " + str(datetime.now()))
        logger.error("API Error") 


# Function to Send Tweets /  This function called in globalDataTweet() function
def sendTweet(distName,confirmed,recovered,deceased,tested):
    tweetText = (f"🦠 #Covid19 Updates ಕರ್ನಾಟಕ 🦠\n\n"
                f"🚩ಜಿಲ್ಲೆ - {distName}\n"
                f"😟ದೃಢಪಟ್ಟಿರುವ ಪ್ರಕರಣಗಳು - {confirmed}\n"
                f"😀ಚೇತರಿಸಿಕೊಂಡ ಪ್ರಕರಣಗಳು - {recovered}\n"
                f"😭ಸಾವಿನ ಪ್ರಕರಣಗಳು - {deceased}\n"
                f"🩺ಪರೀಕ್ಷಿಸಲಾದ ಪ್ರಕರಣಗಳು - {tested}\n\n"
                f"#CoronaVirus #CoronaUpdates #Karnataka #KarnatakaFightsCorona #FollowKarnataka #Kannada")

    if api.update_status(tweetText):
        print('tweeted')
    else:
        print('error in tweepy')
    print(tweetText)

#Create Schedules
schedule.every().day.at("10:33").do(DistrictDataTweet)
schedule.every().day.at("18:37").do(DistrictDataTweet)

#Run Infinite Loop for Schedule

while True:
    try:
        schedule.run_pending()
    except tweepy.TweepError as error:
        print(error)
    time.sleep(3600)
