#!/usr/bin/env python
# -*- coding:utf-8 -*-
u'''
終電情報を収集するプログラム
'''
from bs4 import BeautifulSoup
import sqlite3
import urllib
import urllib2
import time
import sys
import random
import datetime


def storing_syuden_info(from_st,to_st,syuden_time,route,route_times,route_railways,is_holiday):
    u'''入力された終電情報をsqliteに書き込むプログラム'''
    conn = sqlite3.connect('./syuden.sqlite')

    c = conn.cursor()

    # テーブルがなければ作成
    try:
        c.execute(u"""create table syuden
            (
            id integer primary key autoincrement,
            from_st text,
            to_st text,
            syuden_time text,
            route text,
            route_times text,
            route_railways text,
            is_holiday integer
            )""")
    except:
        #print "you already made syuden table"
        pass

    c.execute(u"""insert into syuden
        values (
        NULL,
        '{0}',
        '{1}',
        '{2}',
        '{3}',
        '{4}',
        '{5}',
        {6}
        )""".format(from_st,to_st,syuden_time,route,route_times,route_railways,is_holiday))
    conn.commit()
    c.close()


def harvest(filename):
    u'''
    駅名のペアが書かれたファイルを読み込んで、終電情報を保存するプログラム
    
    ファイルの内容:カンマ区切りの駅名
    六本木,越谷
    六本木,北千住
    ...

    '''
    import socket
    socket.setdefaulttimeout(30)
    with open(filename,'r') as f:
        station_list = [ line.decode('utf-8').replace('\n','') for line in f.readlines()]
    count = 0
    for station_pair in  station_list:
        st1, st2 = station_pair.split(',')
        count += 1
        time.sleep(2+random.randint(1,5)) # 期待値は5秒
        print u"count:{0},{1},{2}".format(count,st1,st2)
        try:
            # 休日の終電情報を取得
            syuden_infos = scraping_syuden_infos(st1,st2,True)
            if syuden_infos:
                storing_syuden_info(*the_latest_syuden_infos(syuden_infos))

            # 平日の終電情報を取得
            syuden_infos = scraping_syuden_infos(st1,st2,False)
            if syuden_infos:
                storing_syuden_info(*the_latest_syuden_infos(syuden_infos))

        except socket.error as e:
            with open('harvest.log', 'a') as f:
                f.write('{0}\t{1}'.format(datetime.datetime.now(), e))
            time.sleep(5*60) # エラーが出たら5分待つ

def the_latest_syuden_infos(syuden_info_list):
    u'''
    複数の終電情報からもっとも遅い終電を取得するプログラム
    入力:
        複数の終電情報のリスト
    出力:
        もっとも遅い終電情報をリストで返す
    '''
    syuden_time_list = [info['syuden_time'] for info in syuden_info_list]
    # 日付をまたいでいるケースの処理+時間の比較のために秒に直す
    def time_to_minutes(time):
        hour, minutes = map(int, time.split(':'))
        if hour < 5:
            hour += 24
        return hour*60+minutes

    # ルートの中で、もっとも遅い終電の情報を取得
    syuden_minutes_list = map(time_to_minutes, syuden_time_list)
    latest_syuden_index = syuden_minutes_list.index(max(syuden_minutes_list))
    latest_syuden_info = syuden_info_list[latest_syuden_index]

    return [
            latest_syuden_info['from_station'],
            latest_syuden_info['to_station'],
            latest_syuden_info['syuden_time'],
            '>'.join(latest_syuden_info['station_list']),
            '>'.join(latest_syuden_info['time_list']),
            '>'.join(latest_syuden_info['railway_list']),
            int(latest_syuden_info['is_holiday'])
            ]



def scraping_syuden_infos(st1,st2,is_holiday=False):
    u'''
    終電情報をスクレイピングするプログラム
    入力:
        st1:出発地
        st2:到着地
        is_holiday:休日フラグ
    出力:
        終電情報のリスト
        終電情報は
        + 出発地(from_station)
        + 到着地(to_station)
        + 終電の時刻(syuden_time)
        + 経路(station_list)
        + 乗り換え時間(time_list)
        + 運行会社(railway_list)
        で構成される辞書
    '''
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
       
    #syuden_list = []
    soup     = BeautifulSoup( response.read() )

    route_list = []
    # 経路を抽出
    for route_detail in soup.find_all('div', 'routeDetail'):
        route_info = {}

        # 休日かどうかの情報を辞書に追加
        route_info['is_holiday'] = is_holiday

        # 駅と時間を取得
        station_list = []
        time_list = []
        err_flag = False
        err_message = None
        for station_info in route_detail.find_all('div','station'):
            try:
                time_list.append(','.join([times.string for times in station_info.find('ul','time').find_all('li')]))
            except Exception as e:
                err_flag = True
                err_message = str(e)

            try:
                if station_info.dl.dt.a:
                    station_list.append(station_info.dl.dt.a.string)
                else:
                    station_list.append(station_info.dl.dt.string)
            except Exception as e:
                err_flag = True
                err_message = str(e)

        route_info['station_list'] = station_list
        route_info['time_list'] = time_list

        # 発車駅と到着駅情報を辞書に追加
        route_info['from_station'] = station_list[0]
        route_info['to_station'] = station_list[-1]

        # 終電の発車時刻を取得
        route_info['syuden_time'] = time_list[0]

        # 路線を取得
        railway_list = []
        for railway_info in route_detail.find_all('li','transport'):
            try:
                railway_list.append(railway_info.div.contents[2].strip())
            except Exception as e:
                err_flag = True
                err_message = str(e)

        if err_flag:
            print '{0},{1}'.format(station_list[0],station_list[1])
            print err_message

        route_info['railway_list'] = railway_list

        route_list.append(route_info)

    return route_list

if __name__ == '__main__':
    #storing_syuden_info(*the_latest_syuden_infos(scraping_syuden_infos(u'宮の坂',u'泉市民体育館(立川バス)',is_holiday=True)))
    harvest(sys.argv[1])
