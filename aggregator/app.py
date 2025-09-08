from flask import Flask, jsonify, request
import requests
import os
import xmltodict
import json
import time

user = os.getenv('BEEMINDER_USER')
auth_token = os.getenv('BEEMINDER_AUTH_TOKEN')
todoist_token = os.getenv('TODOIST_TOKEN')

app = Flask(__name__)

@app.route('/')
def home():
    return "Aggregator running!"

@app.route('/bgg-hotness')
def get_bgg_hotness():
    url = "https://boardgamegeek.com/xmlapi2/hot?type=boardgame"
    resp = requests.get(url)
    if resp.status_code == 200:
        data_dict = xmltodict.parse(resp.content)
        games_raw = data_dict["items"]["item"]
        games = []
        for g in games_raw:
            game = {
                "id": g.get("@id"),
                "rank": g.get("@rank"),
                "name": g.get("name", {}).get("@value", ""),
                "yearpublished": g.get("yearpublished", {}).get("@value", ""),
                "thumbnail": g.get("thumbnail", {}).get("@value", ""),
            }
            games.append(game)
        wrapped_data = {
            "specials": {
                "id": "cat_specials",
                "name": "Specials",
                "items": games
            }
        }
    return jsonify(wrapped_data)

@app.route('/bgg-lastplays')
def get_bgg_lastplays():
    url = "https://boardgamegeek.com/xmlapi2/plays?username=trispancakes"
    resp = requests.get(url)
    if resp.status_code == 200:
        data_dict = xmltodict.parse(resp.content)
        plays_raw = data_dict["plays"]["play"]
        plays = []
        for p in plays_raw:
            players = p.get("players", {}).get("player", [])
            if isinstance(players, dict):
                players = [players]
            player_names = [player.get("@name", "") for player in players]
            number_players = len(players)
            play = {
                "date": p.get("@date"),
                "name": p.get("item", {}).get("@name", ""),
                "id": p.get("item", {}).get("@objectid", ""),
                "players": player_names,
                "num_players": number_players
            }
            plays.append(play)
        wrapped_data = {
            "specials": {
                "id": "cat_specials",
                "name": "Specials",
                "items": plays
            }
        }
    return jsonify(wrapped_data)

import re
@app.route('/goodreads-reading')
def get_currently_reading():
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
     Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.goodreads.com/",
    }
    url = "https://www.goodreads.com/review/list_rss/9476155?shelf=currently-reading"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        rss = xmltodict.parse(resp.content)
        items = rss['rss']['channel']['item']
        if isinstance(items, dict):
            items = [items]
        books = []
        for item in items:
            book_name = item.get('title', '').strip()
            book_link = item.get('link', '').strip()
            book_cover = item.get('book_large_image_url', '').strip()
            description = item.get('description', '')
            match = re.search(r'author:\s*(.*?)<br/>', description)
            author = match.group(1).strip() if match else ''
            item = {
                "book_name": book_name,
                "book_link": book_link,
                "book_cover": book_cover,
                "author": author
            }
            books.append(item)

        wrapped_data = {
            "specials": {
                "id": "cat_specials",
                "name": "Specials",
                "items": books
            }
        }
    return jsonify(wrapped_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)