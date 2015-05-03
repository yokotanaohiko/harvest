#!/usr/bin/env python
# -*- coding:utf-8 -*-
u'''
終電のデータベースを収集するためのデプロイプログラム
+ 環境設定
+ ファイル配布
+ プログラム実行したい(TODO)
+ 結果を収集したい(TODO)

'''
from fabric.api import task, run, env, put, parallel, sudo
from fabric.contrib.files import exists
from itertools import cycle, permutations
import os
import re

STATION_LIST_FILENAME = 'dealiased_result.txt'
env.use_ssh_config = True

@task
def set_hosts():
    u'''デプロイ先のホストを設定する'''
    env.hosts = [
            'ec2-54-213-222-80.us-west-2.compute.amazonaws.com',
            'ec2-54-213-221-97.us-west-2.compute.amazonaws.com',
            'ec2-54-213-219-9.us-west-2.compute.amazonaws.com',
            'ec2-54-213-218-248.us-west-2.compute.amazonaws.com',
            'ec2-54-213-217-136.us-west-2.compute.amazonaws.com',
            'ec2-54-213-216-235.us-west-2.compute.amazonaws.com',
            'ec2-54-213-214-143.us-west-2.compute.amazonaws.com',
            'ec2-54-213-214-68.us-west-2.compute.amazonaws.com',
            'ec2-54-213-214-9.us-west-2.compute.amazonaws.com',
            'ec2-54-213-213-213.us-west-2.compute.amazonaws.com'
            ]

@task
@parallel
def hello():
    u'''ホストが設定できているかどうか確認'''
    run('echo hello world')

@task
def install_tmux():
    u'''centosにtmuxをインストール'''
    bin_list = run('ls /bin')
    cmd_list = re.split(r'\W+', bin_list.replace('\t', ''))
    if 'wget' not in cmd_list:
        sudo('yum install wget')
    if 'tmux' not in cmd_list:
        sudo('wget http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm')
        sudo('rpm -ivh rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm')
        sudo('yum -y install tmux')

@task
def install_beautifulsoup():
    u'''centosにpipとbeautifulsoupをインストール'''
    bin_list = run('ls /bin')
    cmd_list = re.split(r'\W+', bin_list.replace('\t', ''))
    if 'pip' not in cmd_list:
        sudo('easy_install pip')

    sudo('pip install beautifulsoup4')

@task
def distribute_files():
    u'''プログラムとデータをサーバに配布する'''
    distribute_programs()
    distribute_station_list(STATION_LIST_FILENAME)

@task
def distribute_programs():
    u'''プログラムをサーバに配布する'''
    put('harvest_syuden.py', 'station/harvest_syuden.py')

def distribute_station_list(station_list_filename):
    u'''駅のリストデータ等分割してホストサーバに配布する'''
    NUM_HOSTS = len(env.hosts)

    # TODO:ファイル分割をすべきかどうかの条件分岐をもっと良いものに
    if not os.path.exists('split_0'):
        split_file(station_list_filename, NUM_HOSTS)

    if not exists('./station'):
        run('mkdir -m 777 station')

    # TODO:ホストによって配布するファイルを変えたい
    for split_filename in [ 'split_{0}'.format(i) for i in range(NUM_HOSTS)]:
        put(split_filename, 'station/'+split_filename)

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
    for line, id in zip(permutations(lines,2), cycle(range(split_num))):
        with open(split_filename_template.format(id), 'a') as f:
            f.write(','.join(line)+'\n')

    return [split_filename_template.format(id) for id in range(split_num)]

