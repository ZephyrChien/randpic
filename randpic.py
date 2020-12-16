#!/usr/bin/env python3
# coding:utf-8
import io
import flask
import random
import requests
from bs4 import BeautifulSoup
import config

app=flask.Flask(__name__)

def secure_get(url):
    try:
        resp=requests.get(url,timeout=3)
    except:
        return None
    else:
        return resp

def get_url(url):
    if url.endswith('/'):
        resp=secure_get(url)
        if not resp:
            return ''
        soup=BeautifulSoup(resp.text,'lxml')
        links=soup.find_all('a')
        if len(links) <= 1:
            return ''
        else:
            links.pop(0)        
            randlink=links[random.randint(0,len(links)-1)]
            path=randlink.get('href')
            if not path:
                return ''
            return get_url(url+path)
    else:
        return url

@app.route(config.PATH)
def api():
    url=get_url(config.URL)
    if not url:
        return flask.abort(404)
    resp=requests.get(url)
    if not resp:
        return flask.abort(404)
    return flask.send_file(io.BytesIO(resp.content),mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=False)
