#!/usr/bin/python3
# -*- coding:utf8 -*-

import time, sys, datetime, os, subprocess

from danmu import DanMuClient


def pp(msg):
    return msg  #(msg.decode('utf8').encode('gbk'))


##1969843
url = 'https://www.panda.tv/24163'
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
    pathF = 'mvs/%s/%s' % (JSONFILE['name'], JSONFILE['name'])
    path = 'mvs/%s' % JSONFILE['name']
    subprocess.call([
        "python3", 
        "niconvert.pyw", pathF + ".xml", 
        "+r", "1600x900", 
        "-o", path
    ], True)
    JSONFILE['stream'].terminate()
    subprocess.call([
        'ffmpeg', '-i', 
        'mvs/%s/%s.flv' % (JSONFILE['name'], JSONFILE['name']), 
        '-vcodec', 'libx264', 
        '-crf', '23.5', 
        '-vf', 'ass=mvs/%s/%s.ass' % (JSONFILE['name'], JSONFILE['name'])
    ], True)
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
    print(pp('%s:[%s] %s' % (time.time(), msg['NickName'], msg['Content'])))
    if (JSONFILE['file'] != None):
        JSONFILE['file'].write(u'<d p="%s,1,25,16777215,0,0,0,0">%s</d>\n' %
                               (time.time() - JSONFILE['time'],
                                pp(msg['Content'])))


@dmc.gift
def gift_fn(msg):
    print(pp('[%s] sent a gift!' % msg['NickName']))


@dmc.other
def other_fn(msg):
    print(pp('Other message received'))


dmc.start(blockThread=True)
