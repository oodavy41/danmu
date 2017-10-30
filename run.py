#!/usr/bin/python3
# -*- coding:utf8 -*-

import time, sys, datetime, os, subprocess, signal

from danmu import DanMuClient


def pp(msg):
    return msg  #(msg.decode('utf8').encode('gbk'))


##1969843
url = 'https://www.panda.tv/10300'
dmc = DanMuClient(url)
if not dmc.isValid(): print('Url not valid')

XMLhead = u'''
<i>%s
<chatserver>chat.bilibili.com</chatserver>
<chatid>0</chatid>
<mission>0</mission>
<maxlimit>100000</maxlimit>
<source>k-v</source>

'''

JSONFILE = {'name': '', 'time': 0.0, 'file': None, 'stream': None}

#danmu{time:unixtime,message:text}
#ffmpeg -i Lantern.mp4 -vcodec libx264 -preset fast -crf 20 -vf "ass=Lantern.ass" out.mp4
#ffmpeg -i 2017-10-26.flv -vcodec libx264 -crf 23.5 -strict -2 2017-10-26.mp4


def onOpenFun():
    global JSONFILE
    global url
    JSONFILE['name'] = datetime.datetime.now().strftime('%Y-%m-%d')
    JSONFILE['time'] = time.time()
    if not os.path.exists('mvs/' + JSONFILE['name']):
        os.makedirs('mvs/' + JSONFILE['name'])
    JSONFILE['file'] = open('mvs/%s/%s.xml' % (JSONFILE['name'],
                                               JSONFILE['name']), 'w', -1,
                            "utf8")
    JSONFILE['file'].write(XMLhead % JSONFILE['time'])

    JSONFILE['stream'] = subprocess.Popen([
        'you-get', '-o',
        'mvs/%s' % JSONFILE['name'], '-O', JSONFILE['name'], url
    ])


def onCloseFun():
    global JSONFILE
    JSONFILE['file'].write('</i>\n')
    JSONFILE['file'].close()
    pathF = 'mvs/%s/%s.xml' % (JSONFILE['name'], JSONFILE['name'])
    path = 'mvs/%s/' % JSONFILE['name']
    subprocess.call(
        ["python", "niconvert.pyw", pathF, "+r", "1600x900", "-o", path])
    JSONFILE['stream'].terminate()
    subprocess.call([
        'ffmpeg', '-threads', 'auto', '-i',
        'mvs/%s/%s.flv' % (JSONFILE['name'], JSONFILE['name']), '-vcodec',
        'libx264', '-strict', '-2', '-crf', '23.5', '-vf',
        'ass=mvs/%s/%s.ass' % (JSONFILE['name'], JSONFILE['name']),
        'mvs/%s/%s.mp4' % (JSONFILE['name'], JSONFILE['name'])
    ])
    JSONFILE = {'name': '', 'time': 0.0, 'file': None, 'stream': None}


@dmc.onState
def state_change(msg):
    print(pp("Live State Change: " + str(msg['value'])))
    global JSONFILE
    if (msg['value']):
        if (JSONFILE['file'] != None):
            onCloseFun()
        onOpenFun()
    else:
        onCloseFun()


@dmc.danmu
def danmu_fn(msg):
    global JSONFILE
    print(pp('%s:[%s] %s' % (time.time(), msg['NickName'], msg['Content'])))
    if (JSONFILE['file'] != None and not JSONFILE['file'].closed):
        JSONFILE['file'].write(u'<d p="%s,1,25,16777215,0,0,0,0">%s</d>\n' %
                               (time.time() - JSONFILE['time'],
                                pp(msg['Content'])))
        JSONFILE['file'].flush()


@dmc.gift
def gift_fn(msg):
    print(pp('[%s] sent a gift!' % msg['NickName']))


@dmc.other
def other_fn(msg):
    print(pp('Other message received'))


def lda(*args):
    global JSONFILE
    if (JSONFILE['file'] != None and not JSONFILE['file'].closed):
        onCloseFun()
    exit()


signal.signal(signal.SIGTERM, lda)
signal.signal(signal.SIGINT, lda)
dmc.start(blockThread=True)
