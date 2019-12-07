from flask import Flask,render_template,url_for,request
from flask_bootstrap import Bootstrap
from tweepy import OAuthHandler, API, Stream ,Cursor , TweepError
import flaskr.functions.Tokens as t
import csv
import pandas as pd
import sys
import re
from textblob import TextBlob 
def clean(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())
def get_sentiment(tweet):
    tweet=clean(tweet)
    result = TextBlob(tweet)
    if result.sentiment.polarity > 0:
        return 'positive'
    elif result.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'
def tw_main():
    api=authenticate()
    if request.method == 'GET':
        hashtag = request.args.get('hash')
        filename = "SAMJONES.CSV"
        sentiment=[]
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        filename+='.csv'
        csvFile = open(filename,'a')
        csvWriter = csv.writer(csvFile)
        print(api)
        print("Writing into CSV started")
        n=0
        try:
            for tweet in Cursor(api.search,q=hashtag,count=10,lang="en",since="2014-04-03").items():
                csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
                sentiment.append(get_sentiment(tweet.text))
                n=n+1
                if n==200:
                    break
            positive=sentiment.count('positive')
            negative=sentiment.count('negative')
            neutral=sentiment.count('neutral')
            pos=sentiment.count('positive')/n
            neg=sentiment.count('negative')/n
            neu=sentiment.count('neutral')/n
            res=str(positive)+' '+str(neutral)+' '+str(negative)+' '+str(pos)+' '+str(neu)+' '+str(neg)+' '+str(hashtag)
            print("Finshed Writing ",n)
        except TweepError as e:
            print("The Error is "+str(e))
    return res
def authenticate():
    auth = OAuthHandler(t.CONSUMER_KEY, t.CONSUMER_SECRET)
    auth.set_access_token(t.ACCESS_TOKEN,t.ACCESS_TOKEN_SECRET)
    api = API(auth,wait_on_rate_limit=True)
    return api
