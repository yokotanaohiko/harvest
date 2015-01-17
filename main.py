#!/usr/bin/python
# -*- coding:utf-8 -*-

import json, urllib, urllib2, sys, os
import cgi, cgitb
sys.path.append(os.path.dirname(__file__))
from utils import syuden
from utils import route_manager
reload(sys)
sys.setdefaultencoding('utf-8')

def application(environ, start_response):
  # Get Request(GET) from app
  query = cgi.parse_qsl(environ.get('QUERY_STRING'))
  param_dict = {}
  for params in query:
    param_dict[params[0]] = params[1]

  start_response("200 OK", [('Content-Type','application/json'), ('charset', 'utf-8')])

  rm = route_manager.RouteManager(param_dict['gps_lat'], param_dict['gps_lon'], param_dict['station_lat'], param_dict['station_lon'])

  # あと何分でここを出ないとやばいか
  # ３時間以上余裕があれば {'ret':'notyet'}のみ返す
  try :
    time_of_syuden = syuden.syuden_search(
            param_dict['station_lat'],
            param_dict['station_lon'],
            urllib.unquote(param_dict['neighbor_station'])) 
    time_to_nearest_station = rm.get_duration()
    if time_of_syuden-time_to_nearest_station > 15*60 :
      return json.dumps({'ret': 'notyet'})

    ret = map(str,[int( (time_of_syuden-time_to_nearest_station)/60 ),int( time_of_syuden/60  )])
    ret += rm.get_route()
    return json.dumps({'ret': ','.join(ret)})
  except Exception as e :
    return json.dumps({'ret': 'notyet'})

