#!/usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import sqlite3
import urllib
import urllib2
import re
import time
import sys


def set_stations_syuden(st1,st2,time,flag):
    conn = sqlite3.connect('/home/job/githome/harvest/syuden.sqlite')

    c = conn.cursor()
    #table_exists = c.execute("""
    #  select count(*) from sqlite_master
    #  where type='table' and name='<syuden>'""")
    #if not table_exists.fetchone():
    try:
        c.execute(u"""create table syuden
    (id integer primary key autoincrement,from_st text,to_st text,time text,flag integer)""")
    except:
        #print "you already made syuden table"
        pass

    c.execute(u"""insert into syuden
        values (NULL,'{0}','{1}','{2}',{3})""".format(st1,st2,time,flag))
    conn.commit()
    c.close()

def get_syuden(st1,st2,is_holiday=False):
    headers = {'User-Agent':'Mozilla/5.0(X11; Linux i686) AppleWebKit/534.30(KHTML, like Gec    ko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30'}
    url="http://transit.loco.yahoo.co.jp/search/result"
    if is_holiday:
        day = 27
    else:
        day = 25
    data = {
            'flatlon'   :'', 
            'from'      :st1.encode('utf-8'),
            'tlatlon'   :'',
            'to'        :st2.encode('utf-8'),
            'ym'        :'201412',
            'd'         :day,
            'hh'        :13,    'm2'        :9 ,
            'm1'        :3 ,    'type'      :2 ,
            'ticket'    :'ic',  'al'        :1 ,
            'shin'      :1 ,    'ex'        :1 ,
            'hb'        :1 ,    'lb'        :1 ,
            'sr'        :1 ,    's'         :0 ,
            'expkind'   :1 ,    'ws'        :2 
            }

    req      = urllib2.Request( url, urllib.urlencode(data), headers )
    try:
        response = urllib2.urlopen( req )
    except Exception as e:
        print >> sys.stderr, e
        print >> sys.stderr, "you sent wrong station name"
        #print >> sys.stderr, "st1={0},st2={1}".format(st1,st2)
        return False
        
    soup     = BeautifulSoup( response.read().replace('"+"','') )
    route    = soup.find_all('li','time')
    syuden_candidate = []
    for lll in route :
        if "発" in lll.encode('utf-8') :
            m=re.search("\d{2}:\d{2}",lll.encode('utf-8'))
            if m :
                hour,minute = map(int,m.group().split(':'))
                if hour < 5 : hour += 24
                second = hour*3600+minute*60
                syuden_candidate.append([second,hour,minute]) 

    try:
        syuden = max(syuden_candidate,key=lambda x:x[0])
    except:
        return False
    return "{0}:{1}".format(str(syuden[1]).zfill(2),str(syuden[2]).zfill(2))

def harvest(filename):
    import socket
    socket.setdefaulttimeout(3)
    f = open(filename,'r')
    station_list = [ line.decode('utf-8').replace('\n','') for line in f.readlines()]
    f.close()
    count = 0
    for st1 in  station_list:
        for st2 in station_list:
            if st1==st2:
                continue
            count += 1
            if count <= 23*1805:
                continue
            time.sleep(5)
            print u"count:{0},{1},{2}".format(count,st1,st2)
            try:
                syuden = get_syuden(st1,st2,True)
                if syuden:
                    set_stations_syuden(st1,st2,syuden,0)
                syuden = get_syuden(st1,st2,False)
                if syuden:
                    set_stations_syuden(st1,st2,syuden,1)
            except socket.error as e:
                with open('harvest.log', 'a') as f:
                    f.write('')
                time.sleep(5*60)



if __name__ == '__main__':
    #set_stations_syuden('美加の台','難波','23:01:00',1)
    #print get_syuden(u'三国ヶ丘',u'千早口')
    harvest(sys.argv[1])
