#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib, urllib2, json

class RouteManager() :
  def __init__(self,start_lat=None, start_lon=None, goal_lat=None, goal_lon=None) : 
    self.start_lat =  start_lat 
    self.start_lon =  start_lon
    self.goal_lat  =  goal_lat
    self.goal_lon  =  goal_lon

  def is_coordinate_set(self):
    if self.start_lat and self.start_lon and self.goal_lat and self.goal_lon :
      return True
    else :
      return False

  def set_start_and_goal(self,start_lat, start_lon, goal_lat, goal_lon):
    self.start_lat =  start_lat 
    self.start_lon =  start_lon
    self.goal_lat  =  goal_lat
    self.goal_lon  =  goal_lon

  def get_google_api_response(self):
    print('google_api is called')
    url = 'http://maps.googleapis.com/maps/api/directions/json?origin={0},{1}&destination={2},{3}&sensor=false&mode=walking'.format(self.start_lat,self.start_lon,self.goal_lat,self.goal_lon)
    try:
      req = urllib2.urlopen(url)
      res = json.loads(req.read())
      req.close()
      self.res = res
      return res
    except Exception as e:
      raise Exception('we cannot get google_api responses:'+e)

  def get_duration(self):
    if not self.is_coordinate_set() :
      raise Exception('you have to initialize coordinate to route manager')
    
    try :
      res=self.get_google_api_response() if not hasattr(self,'res') else self.res
      return res['routes'][0]['legs'][0]['duration']['value']
    except Exception as e:
      raise Exception('json decode error in get_duration or \n'+e)

  def get_route(self):
    if not self.is_coordinate_set() :
      raise Exception('you have to initialize coordinate to route manager')

    try :
      res=self.get_google_api_response() if not hasattr(self,'res') else self.res
      step_list = []
      steps = res['routes'][0]['legs'][0]['steps']
      for step in steps:
        step_list.append('{0}:{1}'.format(
          step['start_location']['lat'],
          step['start_location']['lng']))
      step_list.append('{0}:{1}'.format(
        steps[-1]['end_location']['lat'],
        steps[-1]['end_location']['lng']))
      return step_list 
    except Exception as e:
      raise Exception('json decode error in get_duration or \n'+e)

if __name__ == '__main__' :
  rm = RouteManager(35.657420912194,139.700634739871,35.65945,139.701035)
  print(rm.is_coordinate_set())
  #print(rm.get_google_api_response())
  print(rm.get_route())
  print(rm.get_duration())
