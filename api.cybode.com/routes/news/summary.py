from goose3 import Goose
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

get_summary = Blueprint('get_summary', __name__)

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@get_summary.route('/summary')
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