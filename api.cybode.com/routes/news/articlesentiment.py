from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
import os
from goose3 import Goose
import requests

#create blueprint
get_article_sentiment = Blueprint('get_article_sentiment', __name__)

from app import app
from app import headers


API_URL_HATE = "https://api-inference.huggingface.co/models/IMSyPP/hate_speech_en"

def query_hate(payload):
	response = requests.post(API_URL_HATE, headers=headers, json=payload)
	return response.json()

#route creation
@get_article_sentiment.route("/article-sentiment", methods=["GET"])
def articleSentiment():
    url = request.args['url']

    # url = 'https://blogs.jayeshvp24.dev/dive-into-web-design'
    goose = Goose()
    articles = goose.extract(url)
    sentence = articles.cleaned_text[0:500]
    print(sentence)
    output=query_hate({
	"inputs": str(sentence)})
    # print(output[0][0])
    result = {}
    for data in output[0]:
        if data['label'] == "LABEL_0":
            result["ACCEPTABLE"] = data['score']
        elif data['label'] == "LABEL_1":
            result["INAPPROAPRIATE"] = data['score']
        elif data['label'] == "LABEL_2":
            result["OFFENSIVE"] = data['score']
        elif data['label'] == "LABEL_3":
            result["VIOLENT"] = data['score']
    labels = list(result.keys())
    values = list(result.values())


    return jsonify({"labels": labels, "values": values})
            

