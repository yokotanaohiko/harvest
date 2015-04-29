#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib,urllib2,json,re,sys,os
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from station_manager import StationManager

def syuden_search(stlat,stlon,neighbor_stname) :
    filepath = os.path.dirname(__file__)
    sm = StationManager()
    fromst = unicode(sm.nearest_station(stlat,stlon))
    now = datetime.today() 
    #if not fromst :
    #    raise Exception('from your coodinates of nearby station, we cannot find station name ')
    tost = neighbor_stname
    headers = {'User-Agent':'Mozilla/5.0(X11; Linux i686) AppleWebKit/534.30(KHTML, like Gec    ko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30'}
    url="http://transit.loco.yahoo.co.jp/search/result"
    data = {
        'flatlon'   :'', 
        'from'      :fromst.encode('utf-8'),
        'tlatlon'   :'',
        'to'        :tost.encode('utf-8'),
        'ym'        :int('%d%d' %(now.year,now.month)),
        'd'         :now.day,
        'hh'        :13,    'm2'        :9 ,
        'm1'        :3 ,    'type'      :2 ,
        'ticket'    :'ic',  'al'        :1 ,
        'shin'      :1 ,    'ex'        :1 ,
        'hb'        :1 ,    'lb'        :1 ,
        'sr'        :1 ,    's'         :0 ,
        'expkind'   :1 ,    'ws'        :2 
    }
    
    req      = urllib2.Request( url, urllib.urlencode(data), headers )
    response = urllib2.urlopen( req )
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

    syuden = max(syuden_candidate,key=lambda x:x[0])

    now_hour       = now.hour if now.hour >= 5 else now.hour+24
    time_of_syuden = timedelta(hours=syuden[1],minutes=syuden[2])
    time_of_now    = timedelta(hours=now_hour,minutes=now.minute)

    if time_of_syuden > time_of_now :
      return (time_of_syuden-time_of_now).seconds
    else :
      raise Exception('you missed last train error')
      return False

if __name__ == ("__main__") :

    print(syuden_search("35.694515","139.69256",u"東京"))
