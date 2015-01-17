#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib2
import time
import sys
f = open('station20141030free.csv','r')
line = f.readline()
count = 1
while line:
    infos = line.split(',')
    name = infos[2].decode('utf-8').replace(u'地下鉄','').split(u'（')[0].encode('utf-8')
    lat = infos[10]
    lon = infos[9]
    address = infos[7].replace('-','')
    if lon > '139.2226909' and lon <'140.8866101':
        if lat > '34.3938638' and lat < '37.1648687':
            try:
                res = urllib2.urlopen('http://zip.cgis.biz/csv/zip.php?zn={0}'.format(address))
                region = res.read().split(',')[12].replace('"','').decode('euc_jp').encode('utf-8')
                time.sleep(1)
            except Exception as e:
                print >> sys.stderr, e
                print >> sys.stderr, "except name"+name
                print >> sys.stderr, "except region"+region
            print "{0},{1}".format(name,region)
            
            res.close()
            count += 1
    #if count > 10:
    #    break
    line = f.readline()
f.close()
