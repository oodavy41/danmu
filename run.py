#!/usr/bin/python3
# -*- coding:utf8 -*-

import time, sys, datetime, os

from danmu import DanMuClient


def pp(msg):
    return msg  #(msg.decode('utf8').encode('gbk'))


##1969843
dmc = DanMuClient('https://www.douyu.com/126493')
if not dmc.isValid(): print('Url not valid')

XMLhead = '''
<i>%s
<chatserver>chat.bilibili.com</chatserver>
<chatid>0</chatid>
<mission>0</mission>
<maxlimit>100000</maxlimit>
<source>k-v</source>

'''

JSONFILE = {'name': '', 'time': 0.0, 'file': None}

#danmu{time:unixtime,message:text}


def onOpenFun():
    JSONFILE['name'] = datetime.datetime.now().strftime('%Y-%m-%d')
    JSONFILE['time'] = time.time()
    if not os.path.exists('mvs/' + JSONFILE['name']):
        os.makedirs('mvs/' + JSONFILE['name'])
    JSONFILE['file'] = open('mvs/%s/%s.xml' % (JSONFILE['name'],
                                               JSONFILE['name']), 'w', -1,
                            "utf8")
    JSONFILE['file'].write(XMLhead % JSONFILE['time'])


def onCloseFun():
    JSONFILE['file'].write('</i>\n')
    JSONFILE['file'].close()
    pathF = 'mvs/%s/%s' % (JSONFILE['name'], JSONFILE['name'])
    os.system('py niconvert.pyw ' + pathF + '.xml +r 1280x720 -o ' + pathF)
    JSONFILE = {'name': '', 'time': 0.0, 'file': None}


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
        JSONFILE['file'].write('<d p="%s,1,25,16777215,0,0,0,0">%s</d>\n' %
                               (time.time() - JSONFILE['time'],
                                pp(msg['Content'])))


@dmc.gift
def gift_fn(msg):
    print(pp('[%s] sent a gift!' % msg['NickName']))


@dmc.other
def other_fn(msg):
    print(pp('Other message received'))


dmc.start(blockThread=True)
