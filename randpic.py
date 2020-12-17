#!/usr/bin/env python3
# coding:utf-8
import io
import flask
import utils
import config
import threading

app = flask.Flask(__name__)
cache = utils.ImgCache(config.URL,config.CACE_SIZE)
t = threading.Thread(target=cache.crontab,args=(config.FETCH_THREADS,config.FETCH_INTERVAL))

@app.route(config.PATH)
def api():
    url = cache.get()
    if not url:
        return flask.abort(404)
    resp = utils.secure_get(url)
    if not resp:
        return flask.abort(404)
    return flask.send_file(io.BytesIO(resp.content),mimetype='image/jpeg')

if __name__ == '__main__':
    t.start()
    app.run(host=config.HOST, port=config.PORT, debug=False)
