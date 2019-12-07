from flask import Flask,render_template,url_for,request
from flask_bootstrap import Bootstrap
from tweepy import OAuthHandler, API, Stream
import flaskr.functions.Tokens as t
import csv
import pandas as pd
import sys
import os
#import wget
def tm_main():
	#Authentication
	api = authenticate()
	if request.method == 'GET':
                username = request.args.get['username']
                max_tweets = int(request.args.get['count'])
                all_tweets = getTweetsFromUser(username,max_tweets,api)
                media_URLs = getTweetMediaURL(all_tweets)
                downloadFiles(media_URLs,username)
                return ""
def getTweetsFromUser(username,max_tweets,api):
	last_tweet_id, num_images = 0,0
	try:
	    raw_tweets = api.user_timeline(screen_name=username,include_rts=False,exclude_replies=True)
	except Exception as e:
		print (e)
		sys.exit()
	last_tweet_id = int(raw_tweets[-1].id-1)
	if max_tweets == 0:
		max_tweets = 3500
	while len(raw_tweets)<max_tweets:
		sys.stdout.write("\rTweets fetched: %d" % len(raw_tweets))
		sys.stdout.flush()
		temp_raw_tweets = api.user_timeline(screen_name=username,max_id=last_tweet_id,include_rts=False,exclude_replies=True)
		if len(temp_raw_tweets) == 0:
			break
		else:
			last_tweet_id = int(temp_raw_tweets[-1].id-1)
			raw_tweets = raw_tweets + temp_raw_tweets
	print ('\nFinished fetching ' + str(min(len(raw_tweets),max_tweets)) + ' Tweets.')
	return raw_tweets
def getTweetMediaURL(all_tweets):
	tweets_with_media = set()
	for tweet in all_tweets:
		media = tweet.entities.get('media',[])
		if (len(media)>0):
			tweets_with_media.add(media[0]['media_url'])
			sys.stdout.write("\rMedia Links fetched: %d" % len(tweets_with_media))
			sys.stdout.flush()
	return tweets_with_media
def downloadFiles(media_url,username):
	try:
	    os.mkdir('twitter_images')
	    os.chdir('twitter_images')
	except:
                os.chdir('twitter_images')
	try:
	    os.mkdir(username)
	    os.chdir(username)
	except:
		os.chdir(username)
	for url in media_url:
		wget.download(url)
def authenticate():
	auth = OAuthHandler(t.CONSUMER_KEY, t.CONSUMER_SECRET)
	auth.set_access_token(t.ACCESS_TOKEN,t.ACCESS_TOKEN_SECRET)
	api = API(auth)
	return api

