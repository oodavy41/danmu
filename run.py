#!/usr/bin/python3
# -*- coding:utf8 -*-

import time
import sys
import datetime
import os
import subprocess
import signal

from danmu import DanMuClient


def pp(msg):
    return msg  # (msg.decode('utf8').encode('gbk'))


# 1969843
url = 'https://www.panda.tv/10300'
dmc = DanMuClient(url)
if not dmc.isValid():
    print('Url not valid')

XMLhead = u'''
<i>%s
<chatserver>chat.bilibili.com</chatserver>
<chatid>0</chatid>
<mission>0</mission>
<maxlimit>100000</maxlimit>
<source>k-v</source>

'''

JSONFILE = {'name': '', 'time': 0.0, 'file': None, 'stream': None}
DOZENFLAG = 0

# danmu{time:unixtime,message:text}
# ffmpeg -i Lantern.mp4 -vcodec libx264 -preset fast -crf 20 -vf "ass=Lantern.ass" out.mp4
# ffmpeg -i 2017-10-26.flv -vcodec libx264 -crf 23.5 -strict -2 2017-10-26.mp4


def onOpenFun():
    global JSONFILE, url, DOZENFLAG
    if(DOZENFLAG == 0):
        JSONFILE['name'] = datetime.datetime.now().strftime('%Y-%m-%d')
    JSONFILE['time'] = time.time()
    if not os.path.exists('mvs/' + JSONFILE['name']):
        os.makedirs('mvs/' + JSONFILE['name'])
    JSONFILE['file'] = open('mvs/%s/%s.xml' % (JSONFILE['name'],
                                               JSONFILE['name'] + '|%d|' % DOZENFLAG), 'w', -1,
                            "utf8")
    JSONFILE['file'].write(XMLhead % JSONFILE['time'])

    JSONFILE['stream'] = subprocess.Popen([
        'you-get', '-o',
        'mvs/%s' % JSONFILE['name'], '-O', JSONFILE['name'] +
        '|%d|' % DOZENFLAG, url
    ])


def onCloseFun():
    global JSONFILE, DOZENFLAG
    JSONFILE['file'].write('</i>\n')
    JSONFILE['file'].close()
    pathF = 'mvs/%s/%s' % (JSONFILE['name'],
                           JSONFILE['name'] + '|%d|' % DOZENFLAG)
    path = 'mvs/%s/' % JSONFILE['name']
    subprocess.call(
        ["python3", "niconvert.pyw", '%s.xml' % pathF, "+r", "1600x900", "-o", path])
    JSONFILE['stream'].terminate()
    subprocess.Popen([
        'ffmpeg', '-threads', 'auto', '-i',
        '%s.flv' % pathF, '-vcodec',
        'libx264', '-strict', '-2', '-crf', '23.5', '-vf',
        'ass=%s.ass' % pathF,
        '%s.mp4' % pathF
    ])
    DOZENFLAG += 1
    JSONFILE = {'name': '', 'time': 0.0, 'file': None, 'stream': None}


@dmc.onState
def state_change(msg):
    print(pp("Live State Change: " + str(msg['value'])))
    global JSONFILE, DOZENFLAG
    if (msg['value']):
        if (JSONFILE['file'] is not None):
            onCloseFun()
        onOpenFun()
    else:
        onCloseFun()
    DOZENFLAG = 0


@dmc.danmu
def danmu_fn(msg):
    global JSONFILE
    if(msg['Content'].find('[:') != -1):
        return
    print(pp('%s:[%s] %s' % (time.time(), msg['NickName'], msg['Content'])))
    if (JSONFILE['file'] is not None and not JSONFILE['file'].closed):
        JSONFILE['file'].write(u'<d p="%s,1,25,16777215,0,0,0,0">%s</d>\n' %
                               (time.time() - JSONFILE['time'],
                                pp(msg['Content'])))
        JSONFILE['file'].flush()
        if(time.time() - JSONFILE['time'] > 3600):
            onCloseFun()
            onOpenFun()
            print('one hour cut')


@dmc.gift
def gift_fn(msg):
    print(pp('[%s] sent a gift!' % msg['NickName']))


@dmc.other
def other_fn(msg):
    print(pp('Other message received'))


def lda(*args):
    global JSONFILE
    if (JSONFILE['file'] is not None and not JSONFILE['file'].closed):
        onCloseFun()
    exit()


signal.signal(signal.SIGTERM, lda)
signal.signal(signal.SIGINT, lda)
dmc.start(blockThread=True)
