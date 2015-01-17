#!/usr/bin/python
# -*- coding:utf-8 -*-
import json,codecs
from collections import defaultdict

def view_geostation() :
    f = open("geostation.json","r")
    geost = json.loads(r.read())
    f.close()

    for layer1 in geost :
        for layer2 in geost[layer1] :
            

def generate_geostation() :
    f = open('stationgeo.json',"r") 
    stgeo = json.loads(f.read())
    f.close()
    f = open('stationname.json','r')
    stations = json.loads(f.read())
    f.close()
    
    revdict = defaultdict(dict)
    for stname in stgeo :
        coordinate = map(str,stgeo[stname]["coordinates"])
        revdict[coordinate[0]][coordinate[1]]={}
        revdict[coordinate[0]][coordinate[1]]["uri"]=stname

        for station in stations :
            if station["owl:sameAs"]==stname :
                revdict[coordinate[0]][coordinate[1]]["name"] = station["dc:title"]

    f = codecs.open("geostation.json","w","utf-8") 
    f.write(json.dumps(revdict,ensure_ascii=False))
    f.close()

if __name__ == ("__main__") :


