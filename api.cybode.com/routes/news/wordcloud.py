from flask import send_file, jsonify, request, Blueprint
from goose3 import Goose
import requests
from app import app
from app import headers
from wordcloud import WordCloud
import matplotlib.pyplot as plt


API_URL = "https://api-inference.huggingface.co/models/valurank/distilroberta-propaganda-2class"


get_wordcloud = Blueprint('get_wordcloud', __name__)


def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

@get_wordcloud.route('/wordcloud')
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
    