from flask import app, jsonify, request, Blueprint
from goose3 import Goose
import requests
from app import app
from app import headers

API_URL_PROP = "https://api-inference.huggingface.co/models/valurank/distilroberta-propaganda-2class"

get_propaganda = Blueprint('get_propaganda', __name__)

def queryprop(payload):
	response = requests.post(API_URL_PROP, headers=headers, json=payload)
	return response.json()

@get_propaganda.route('/propaganda')
def propaganda():
    url = request.args['url']
    goose = Goose()
    articles = goose.extract(url)
    output = queryprop({
	"inputs":  articles.cleaned_text[0:600]
    })
    
    yes = output[0][0]['score']
    no = 1 - yes
    return jsonify({"yes": yes, "no": no})