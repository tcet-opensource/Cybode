from io import BytesIO
from flask import Flask, jsonify
import os
from config import Config
# import snscrape.modules.instagram as snsinsta
from dotenv import load_dotenv
from flask import request,jsonify
import snscrape.modules.twitter as snstwitter
from snscrape.modules.twitter import TwitterSearchScraper, TwitterSearchScraperMode
import requests
import csv
from goose3 import Goose
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
import json
import plotly
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import base64
import pandas as pd
# from flask import send_file
from flask import send_file
import datetime
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from api.cybode.com.routes.news.authenticity import auth_blueprint 


app = Flask(__name__)
app.register_blueprint(auth_blueprint)

twitterData = None
queryString = None

# print(type(twitterData))

load_dotenv()

print(os.getenv("HUGGINGFACE_API"))


@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

#get tweets associated with topic of the news article [status - 405]
@app.route('/twitter')
def twitter():
    query = request.args['query']
    retweet = 0
    likecount = 0
    hashtags = set([])
    i=0
    global twitterData
    global queryString
    print("Url: Twitter, data: ", twitterData)
    print("Url: Twitter, query: ", queryString)

    twitterData = snstwitter.TwitterSearchScraper(query).get_items()
        
    for tweet in twitterData: 
        print("looping through tweets")
        print(vars(tweet)) 
        likecount += tweet.likeCount
        retweet += tweet.retweetCount + tweet.quoteCount
        if(tweet.hashtags != None):
            for h in tweet.hashtags:
                hashtags.add(h)
        
        i+= 1
        
        if(i==200):
            break
        
    tweets = {"likecount":likecount,"retweet":retweet,"hashtags":list(hashtags),"count":i}
    print(tweets)
    return jsonify({'result':tweets})

#just a random route lol
@app.route('/elonchutiya69')
def xyz():
    query = request.args['query']
    tweets = []
    for tweet in snstwitter.TwitterProfileScraper(query).get_items():
        tweets.append(tweet.date)
    return tweets


#API resources for models
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": "Bearer " +  os.getenv('HUGGINGFACE_API') }
API_URL_PROP = "https://api-inference.huggingface.co/models/valurank/distilroberta-propaganda-2class"
API_URL_HATE = "https://api-inference.huggingface.co/models/IMSyPP/hate_speech_en"


#payloads are here
def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def queryprop(payload):
	response = requests.post(API_URL_PROP, headers=headers, json=payload)
	return response.json()

def query_hate(payload):
	response = requests.post(API_URL_HATE, headers=headers, json=payload)
	return response.json()


#get twitter sentiments associated with the news article [status - 404]
@app.route('/sentiment')
def sentiment():
    query = request.args['query']
    retweet = 0
    likecount = 0
    hashtags = []
    senti=[]
    i=0
    positive=0
    negative=0
    neutral=0
    global twitterData
    global queryString
    print("Url: Sentiment, data: ", twitterData)
    # if twitterData is None:
    #     twitterData = snstwitter.TwitterSearchScraper(query).get_items()
    #     queryString = query
    # else:
    #     if queryString != query:
    #         twitterData = snstwitter.TwitterSearchScraper(query).get_items()
    #         queryString = query
    twitterData = snstwitter.TwitterSearchScraper(query).get_items()
        
    for tweet in twitterData: 
        if tweet.lang=="en":
            i+=1
            if(i==200):
                break
            sentence= tweet.rawContent
            print(sentence)
            sid_obj = SentimentIntensityAnalyzer()
            sentiment_dict = sid_obj.polarity_scores([sentence])
            print(sentiment_dict['neg']*100, "% Negative")
            print(sentiment_dict['pos']*100, "% Positive")
            print("Review Overall Analysis", end = " ") 
            if sentiment_dict['compound'] >= 0.05 :
                positive+=1
            elif sentiment_dict['compound'] <= -0.05 :
                negative+=1
            else :
                neutral+=1
    senti={"positive":positive, "negative":negative, "neutral":neutral}
    labels = list(senti.keys())
    values = list(senti.values())
        
    return {"labels":labels, "values":values}


#summarize the news article [status - 200]
@app.route('/summary')
def summary():
    try:

        url = request.args['url']
        goose = Goose()
        articles = goose.extract(url)
        output = query({
        "inputs":  articles.cleaned_text
        })
        print(output)
    except:
        return "Please put the relevant text article"

    return jsonify({"result": output[0]['summary_text']})

#highlight key segments of the news article [status - 200]
@app.route('/wordcloud')
def plotly_wordcloud2():
    url = request.args['url']
    goose = Goose()
    articles = goose.extract(url)
    text = articles.cleaned_text
    wordcloud = WordCloud(width=1280, height=853, margin=0,
                      colormap='Blues').generate(text)
    wordcloud.to_file("./wordcloud.png")
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.margins(x=0, y=0)

    return send_file("./wordcloud.png", mimetype='image/png')
    

#check the authentic source of the news article [status - 200]
# @app.route('/authenticity')
# def auth():
#     url = request.args['url']
#     lis = []
#     df = pd.read_csv('blacklist.csv')
#     for i in range(len(df)):
#         lis.append(df.loc[i, "MBFC"])

#     for l in lis:
#         if(url.__contains__(l)):
#             return {"authentic":False}

#     return { "authentic": True }

#detect twitter bot activity of the news article [status - 500]
@app.route('/bot-activity')
def botActivity():
    url = request.args['url']
    i=0
    usernames = []
    time = []
    finalusername = []
    for tweet in snstwitter.TwitterSearchScraper(url).get_items():
        usernames.append(tweet.user.username)
        time.append(tweet.date)
        if(i==150):
            break
        i+=1

    flag = False
    for i in range(len(time)-1):
        a = time[i]
        b = time[i+1]
        c = a-b
        if(c.seconds <= 60):            
            finalusername.append(usernames[i+1])

    print("username: ", finalusername)
    if(len(finalusername) > 3):
        flag = True
    return jsonify({"bots":list(set(finalusername)),"flag":flag})

#register blueprints for routes here look at the example below for article sentiment route
from routes.news.articlesentiment import get_article_sentiment
app.register_blueprint(get_article_sentiment)

from routes.social.youtubedata import get_yt_comment
app.register_blueprint(get_yt_comment)

from routes.news.propaganda import get_propaganda
app.register_blueprint(get_propaganda)

#to resolve circular imports
app.config.from_object(Config)

if __name__ == '__main__':
    app.run(debug=True)

