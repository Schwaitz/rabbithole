from flask import Flask, request, render_template, json
import requests
from html import unescape
import string

import app_config as app_config

app = Flask(__name__)

app.config['TESTING'] = False
app.config['SECRET_KEY'] = app_config.SECRET_KEY
app.url_map.strict_slashes = False

host = app_config.api_host

def get_talents():
    talents_file = open('static/talents.json', 'r', encoding='utf-8')
    talent_data = json.loads(talents_file.read())
    talents_file.close()
    return talent_data


@app.context_processor
def utility_processor():
    def format_title(title):
        printable = set(string.printable)
        title = ''.join(filter(lambda x: x in printable, title))
        return title

    def cut_description(desc):
        if len(desc) > 1000:
            desc = desc[:1000]
            desc = desc + "..."

        printable = set(string.printable)
        desc = ''.join(filter(lambda x: x in printable, desc))
        return desc

    def cut_channel_description(desc):
        if len(desc) > 750:
            desc = desc[:750]
            desc = desc + "..."

        printable = set(string.printable)
        desc = ''.join(filter(lambda x: x in printable, desc))
        return desc

    return dict(format_title=format_title, cut_description=cut_description, cut_channel_description=cut_channel_description)


@app.route('/')
def index():
    return render_template('index.html', title="Rabbithole")



@app.route('/channels', methods=['GET'])
def channels():
    params = {'format': 'json'}
    r = requests.get(host + '/channels', params=params).json()
    count = len(r)
    return render_template('channels.html', channel_data=r, channel_count=count)


@app.route('/channels/<id>', methods=['GET'])
def channel(id):
    params = {'format': 'json'}
    r = requests.get(host + '/channels/' + id + '/', params=params).json()
    return render_template('channel.html', channel_id=r['channel_id'], channel_title=r['channel_title'], channel_description=r['channel_description'], channel_thumbnail_url=r['channel_thumbnail_url'])
    # return r


@app.route('/videos', methods=['GET'])
def videos():
    params = {'format': 'json'}
    r = requests.get(host + '/videos', params=params).json()
    count = len(r)
    return render_template('videos.html', video_data=r, video_count=count)


@app.route('/videos/<id>', methods=['GET'])
def video(id):
    params = {'format': 'json'}
    r = requests.get(host + '/videos/' + id + '/', params=params).json()
    player_fixed = unescape(r['video_player'])
    print(player_fixed)
    return render_template('video.html', video_id=r['video_id'], video_title=r['video_title'], video_description=r['video_description'],
                           video_likes=r['video_likes'],
                           video_dislikes=r['video_dislikes'],
                           video_views=r['video_views'],
                           video_comments=r['video_comments'],
                           video_thumbnail_url=r['video_thumbnail_url'], video_player=player_fixed)
    # return r


@app.route('/talents', methods=['GET'])
def talents():
    talent_data = get_talents()

    count = len(talent_data)
    return render_template('talents.html', talent_data=talent_data, talent_count=count)


@app.route('/talents/<name>', methods=['GET'])
def talent(name):
    talents = get_talents()
    match = {}

    found = False
    for t in talents:
        if str(name).lower() == t['name'] or str(name).lower() in t['aliases']:
            match = t
            found = True
            break

    if found:
        params = {'format': 'json'}
        r = requests.get(host + '/videos', params=params).json()

        matched_videos = []
        for v in r:
            if match['name'] in v['video_title'].lower() or any(alias in v['video_title'].lower() for alias in match['aliases']):
                matched_videos.append(v)

        count = len(matched_videos)

        return render_template('talent.html', name=match['full_name'], matched_videos=matched_videos, match_count=count)

    else:
        return render_template('404.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
