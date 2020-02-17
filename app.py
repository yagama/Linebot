import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
import urllib.request
import urllib.parse
import json
from googleapiclient.discovery import build
# from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
DEVELOPER_KEY = 'AIzaSyDKQzkRv8pPGJINkaZ-I5YbjpJNeNyPngk'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(q=options, part='id,snippet', maxResults=11).execute()

    content = ""

    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            content += '{}\nhttps://youtu.be/{}\n\n'.format(search_result['snippet']['title'], search_result['id']['videoId'])

    return content

def avgle(event):
	AVGLE_SEARCH_VIDEOS_API_URL = 'https://api.avgle.com/v1/jav/{}/{}?limit={}'
	query = event
	page = 0
	limit = 5
	response = json.loads(urllib.request.urlopen(AVGLE_SEARCH_VIDEOS_API_URL.format(urllib.parse.quote_plus(query), page, limit)).read().decode())
	#print(response)
	content = ""
	if response['success']:
		for i in range(0,len(response["response"]["videos"])):
			content += '{}\n{}\n\n'.format(response["response"]["videos"][i]['title'][0:20], response["response"]["videos"][i]['embedded_url'])
	return content



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
 #   print("event.reply_token:", event.reply_token)
 #   print("event.message.text:", event.message.text)
	
    if event.message.text[0:3] == "YT ":
        content = youtube_search(event.message.text[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text[0:3] == "Av ":
        content = avgle(event.message.text[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)


if __name__ == '__main__':
    app.run()
