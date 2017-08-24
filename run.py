import time, sys ,datetime

from danmu import DanMuClient

def pp(msg):
    print(msg.encode(sys.stdin.encoding, 'ignore').
        decode(sys.stdin.encoding))
##1969843
dmc = DanMuClient('https://www.douyu.com/1969843')
if not dmc.isValid(): print('Url not valid')


XMLhead='''
<i>
<chatserver>chat.bilibili.com</chatserver>
<chatid>0</chatid>
<mission>0</mission>
<maxlimit>100000</maxlimit>
<source>k-v</source>

'''

JSONFILE={'name':'','time':0.0,'file':None};
##danmu{time:unixtime,message:text}

@dmc.onState
def state_change(msg):
    pp("Live State Change: "+str(msg['value']))
    global JSONFILE
    if(msg['value']):
        JSONFILE['name']=datetime.datetime.now().strftime('%Y-%m-%d')
        JSONFILE['time']=time.time()
        JSONFILE['file'] = open('mvs/%s.xml' % JSONFILE['name'],'w')
        JSONFILE['file'].write(XMLhead)
    else:
        JSONFILE['file'].write('</i>\n')
        JSONFILE['file'].close()
        JSONFILE={'name':'','time':0.0,'file':None}


@dmc.danmu
def danmu_fn(msg):
    pp('%s:[%s] %s' % (time.time(),msg['NickName'], msg['Content']))
    if(JSONFILE['file']!=None):
        JSONFILE['file'].write('<d p="%s,1,25,16777215,0,0,0,0">%s</d>\n'%(time.time()-JSONFILE['time'],msg['NickName']))
        

@dmc.gift
def gift_fn(msg):
    pp('[%s] sent a gift!' % msg['NickName'])

@dmc.other
def other_fn(msg):
    pp('Other message received')

dmc.start(blockThread=True)
