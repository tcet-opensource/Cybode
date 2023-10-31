from flask import Blueprint, request
import pandas as pd

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/authenticity')
def auth():
    url = request.args.get('url')
    lis = []
    df = pd.read_csv('blacklist.csv')
    for i in range(len(df)):
        lis.append(df.loc[i, "MBFC"])

    for l in lis:
        if url and l in url:
            return {"authentic": False}

    return {"authentic": True}
