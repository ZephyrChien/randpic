#!/usr/bin/env python3
# coding:utf-8

import math
import time
import random
import requests
import threading
from bs4 import BeautifulSoup

def str_to_num(s):
    try:
        n = int(s)
    except ValueError:
        return 0
    else:
        return n

def secure_get(url):
    try:
        resp=requests.get(url,timeout=3)
    except:
        return None
    else:
        return resp

def get_new_url(cmd,old_url):
    i = old_url.index('.jpg')
    old_pic_index = str_to_num(old_url[i-2,i])
    new_pic_index = (old_pic_index + 1) if cmd == 'next' else (old_pic_index - 1)
    new_url = old_url.replace(str(old_pic_index),str(new_pic_index))
    return new_url

class ImgCache():
    def __init__(self,home,size):
        self.lock = threading.Lock()
        self.home = home
        self.size = size
        self.cache = []

    def fetch(self,home):
        resp = secure_get(home)
        if not resp:
            return
        soup = BeautifulSoup(resp.text,'lxml')
        urls = soup.find_all('a')
        if len(urls) < 2:
            return
        urls.pop(0)
        url = urls[random.randint(0,len(urls)-1)]
        path = url.get('href')
        if path.endswith('/'):
            self.fetch(home + path)
        else:
            self.lock.acquire()
            if len(self.cache) >= self.size:
                self.lock.release()
                return
            self.cache.append(home + path)
            self.lock.release()

    def get(self):
        self.lock.acquire()
        url = self.cache.pop()
        self.lock.release()
        return url

    def update(self,threads):
        ts = []
        for _ in range(threads):
            ts.append(threading.Thread(target=self.fetch,args=(self.home,)))
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    
    def crontab(self,threads,interval):
        while True:
            self.lock.acquire()
            l = len(self.cache)
            self.lock.release()
            if l >= self.size:
                time.sleep(interval)
                continue
            for _ in range(math.ceil((self.size - l)/threads)):
                self.update(threads)
            time.sleep(interval)

class History():
    def __init__(self,lifetime):
        self.lock = threading.Lock()
        self.lifetime = lifetime
        self.history = {}
    
    def set(self,id,url):
        self.lock.acquire()
        self.history[id] = {'url':url,'time':time.time()}
        self.lock.release

    def get(self,id):
        self.lock.acquire()
        body = self.history.get(id)
        if not body:
            url = ''
        else:
            url = body['url']
        self.lock.release()
        return url

    def delete(self,id):
        self.lock.acquire()
        del self.history[id]
        self.lock.release()

    def autoclean(self,interval):
        while True:
            self.lock.acquire()
            shortcut = self.history.copy()
            self.lock.release()
            current_time = time.time()
            for key,val in shortcut.items():
                if val['time'] + self.lifetime < current_time:
                    self.delete(key)
            time.sleep(interval)