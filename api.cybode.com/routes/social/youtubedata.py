from flask import Flask, jsonify, Blueprint
from googleapiclient.discovery import build 
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

yt_api = os.getenv('YT_API')

youtube = build('youtube', 'v3', developerKey=yt_api) # Generate API KEY yt_api from Google Cloud Console after enabling youtube api v3 and generating apiKey from credential section

get_yt_comment = Blueprint('get_yt_comment', __name__)

@get_yt_comment.route('/get-youtube-data/<video_id>')
def get_yt_comments(video_id):

  res = youtube.commentThreads().list(
    part='snippet', 
    videoId=video_id,
    order='relevance',
    textFormat='plainText',
    maxResults=500
  ).execute()

  comments = []
  for item in res['items']:
    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
    comments.append(comment)

  return jsonify(comments)