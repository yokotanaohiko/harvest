#!/usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import task, run, env, put, parallel
from itertools import cycle

STATION_LIST_FILENAME = 'dealiased_result.txt'
env.use_ssh_config = True

@task
def set_hosts():
    u'''デプロイ先のホストを設定する'''
    env.hosts = [
#            'ec2-54-213-222-80.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-221-97.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-219-9.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-218-248.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-217-136.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-216-235.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-214-143.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-214-68.us-west-2.compute.amazonaws.com',
#            'ec2-54-213-214-9.us-west-2.compute.amazonaws.com',
            'ec2-54-213-213-213.us-west-2.compute.amazonaws.com'
            ]

@task
@parallel
def hello():
    u'''ホストが設定できているかどうか確認'''
    run('echo hello world')

@task
def distribute_files():
    distribute_station_list(STATION_LIST_FILENAME)

def distribute_station_list(station_list_filename):
    u'''駅のリストデータ等分割してホストサーバに配布する'''
    NUM_HOSTS = len(env.hosts)
    NUM_HOSTS = 10

    split_filename_list = split_file(station_list_filename, NUM_HOSTS)

    hostname = run('hostname')
    host_id = env.hosts.index(hostname)
    run('mkdir -m 777 station')
    put(split_filename_list[host_id], 'station/station_names.txt')
    put('harvest_syuden.py', 'station/station_names.txt')

def split_file(filename, split_num):
    u'''
    filenameという名前のファイルを行ごとに
    split_numの数に分割する

    出力されるファイル名は、
    split_<ファイルid>

    返り値は、分割後のファイル名のリスト
    '''
    with open(filename) as f:
        lines = [line.strip() for line in f]

    split_filename_template = 'split_{0}'
    for line, id in zip(lines, cycle(range(split_num))):
        with open(split_filename_template.format(id), 'a') as f:
            f.write(line+'\n')

    return [split_filename_template.format(id) for id in range(split_num)]
