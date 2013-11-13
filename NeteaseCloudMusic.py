#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-06-07 19:28

@author: Yang Junyong <yanunon@gmail.com>
'''

import md5
import base64
import urllib2
import urllib
import json
import random
import os
import sys

#set cookie
cookie_opener = urllib2.build_opener()
cookie_opener.addheaders.append(('Cookie', 'appver=1.5.2'))
urllib2.install_opener(cookie_opener)

def encrypted_id(id):
    byte1 = bytearray('3go8&$8*3*3h0k(2)2')
    byte2 = bytearray(id)
    byte1_len = len(byte1)
    for i in xrange(len(byte2)):
        byte2[i] = byte2[i]^byte1[i%byte1_len]
    m = md5.new()
    m.update(byte2)
    result = m.digest().encode('base64')[:-1]
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result

def search_artist_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 100,
            'offset': 0,
            'sub': 'false',
            'limit': 10
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    artists = json.loads(resp.read())
    if artists['code'] == 200 and artists['result']['artistCount'] > 0:
        return artists['result']['artists'][0]
    else:
        return None

def search_album_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 10,
            'offset': 0,
            'sub': 'false',
            'limit': 20
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    resp_js = json.loads(resp.read())
    if resp_js['code'] == 200 and resp_js['result']['albumCount'] > 0:
        result = resp_js['result']
        album_id = 0
        if result['albumCount'] > 1:
            for i in range(len(result['albums'])):
                album = result['albums'][i]
                print '[%2d]artist:%s\talbum:%s' % (i+1, album['artist']['name'], album['name'])
            select_i = int(raw_input('Select One:'))
            if select_i < 1 or select_i > len(result['albums']):
                print 'error select'
                return None
            else:
                album_id = select_i-1
        return result['albums'][album_id]
    else:
        return None



def search_song_by_name(name):
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': name,
            'type': 1,
            'offset': 0,
            'sub': 'false',
            'limit': 20
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    resp_js = json.loads(resp.read())
    if resp_js['code'] == 200 and resp_js['result']['songCount'] > 0:
        result = resp_js['result']
        song_id = result['songs'][0]['id']
        if result['songCount'] > 1:
            for i in range(len(result['songs'])):
                song = result['songs'][i]
                print '[%2d]song:%s\tartist:%s\talbum:%s' % (i+1,song['name'], song['artists'][0]['name'], song['album']['name'])
            select_i = int(raw_input('Select One:'))
            if select_i < 1 or select_i > len(result['songs']):
                print 'error select'
                return None
            else:
                song_id = result['songs'][select_i-1]['id']
        detail_url = 'http://music.163.com/api/song/detail?ids=[%d]' % song_id
        resp = urllib2.urlopen(detail_url)
        song_js = json.loads(resp.read())
        return song_js['songs'][0]
    else:
        return None

def get_artist_albums(artist):
    albums = []
    offset = 0
    while True:
        url = 'http://music.163.com/api/artist/albums/%d?offset=%d&limit=50' % (artist['id'], offset)
        resp = urllib2.urlopen(url)
        tmp_albums = json.loads(resp.read())
        albums.extend(tmp_albums['hotAlbums'])
        if tmp_albums['more'] == True:
            offset += 50
        else:
            break
    return albums

def get_album_songs(album):
    url = 'http://music.163.com/api/album/%d/' % album['id']
    resp = urllib2.urlopen(url)
    songs = json.loads(resp.read())
    return songs['album']['songs']

def save_song_to_disk(song, folder):
    name = song['name']
    fpath = os.path.join(folder, name+'.mp3')
    if os.path.exists(fpath):
        return

    song_dfsId = str(song['bMusic']['dfsId'])
    url = 'http://m%d.music.126.net/%s/%s.mp3' % (random.randrange(1, 3), encrypted_id(song_dfsId), song_dfsId)
    #print '%s\t%s' % (url, name)
    #return
    resp = urllib2.urlopen(url)
    data = resp.read()
    f = open(fpath, 'wb')
    f.write(data)
    f.close()

def download_song_by_search(name, folder='.'):
    song = search_song_by_name(name)
    if not song:
        print 'Not found ' + name
        return

    if not os.path.exists(folder):
        os.makedirs(folder)
    save_song_to_disk(song, folder)


def download_album_by_search(name, folder='.'):
    album = search_album_by_name(name)
    if not album:
        print 'Not found ' + name
        return
    
    name = album['name']
    folder = os.path.join(folder, name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    songs = get_album_songs(album)
    for song in songs:
        save_song_to_disk(song, folder)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(0)
    download_album_by_search(sys.argv[1], sys.argv[2])
