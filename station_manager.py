#!/opt/python2.7/bin/python
#-*- coding:utf-8 -*-

import geohash,json,os
from coordinates import Coordinate
class StationManager():
    def __init__(self) :
        pass
    
    def station_name_to_utf8(self,name) :
        if 'odpt' in name :
            filepath = os.path.dirname(__file__)
            f = open(filepath+'/stationname.json','r')
            stnamehash = json.loads(f.read())
            f.close()

            for sthash in stnamehash :
                if name == sthash['owl:sameAs'] :
                    return sthash['dc:title']


    def nearest_station(self,lat,lon) :
        kns_list = self.k_nearest_station(lat,lon)
        distance_list = []
        for kns in kns_list :
            coord = Coordinate()
            coord.set_geojson(kns)
            distance_list.append([
                    coord.distance(lat,lon),
                    kns['name']
                    ])
        if distance_list :
            nearest_station = min(distance_list,key=lambda x: x[0])
        else :
            raise Exception('we cannot find any nearest stations in nearest_station')
        return self.station_name_to_utf8(nearest_station[1])

    def k_nearest_station(self,lat,lon):
        lat = float(lat)
        lon = float(lon)
        filepath = os.path.dirname(__file__)
        now_gh = geohash.encode(lat,lon,precision=7)
        f = open(filepath+'/stationgeohash.json','r')
        gh2stations = json.loads(f.read())
        f.close()

        neighbors_st = []
        neighbors_gh = set()
        if gh2stations.has_key(now_gh):
            neighbors_st.extend(gh2stations[now_gh])
        neighbors_gh.add(now_gh)
        for ii in range(10) :
            if len(neighbors_st) > 5 :break
            tmp_gh = list(neighbors_gh)
            for gh in tmp_gh :
                neighbors_gh = neighbors_gh.union(geohash.neighbors(gh))

            for gh in neighbors_gh :
                if gh2stations.has_key(gh):
                    st_list = gh2stations[gh]
                    for st in st_list :
                        sw = True
                        for nst in neighbors_st :
                            if st['name'] == nst['name'] :
                                sw = False

                        if sw :
                            neighbors_st.append(st)

        return neighbors_st


if __name__ == ('__main__') :
    s=StationManager()
    print(s.nearest_station(35.6566363,139.734713))
