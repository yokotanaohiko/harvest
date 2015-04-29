#!/usr/bin/python
# -*- coding:utf-8 -*-
u'''
以下のようなデータから
```
いずみ中央,神奈川県
いずみ野,神奈川県
おもちゃのまち,栃木県
```

次の形式のデータを生成するプログラム
```
<駅名>(<都道府県>)
```
'''
f = open('uniq_station2.txt','r')
lines = map(lambda x:x.replace('\n',''),f.readlines())
for index in range(len(lines)-1):
    sw = False
    if index > 1:
        if lines[index].split(',')[0] == lines[index-1].split(',')[0]:
            sw = True
    if index < len(lines)-2:
        if lines[index].split(',')[0] == lines[index+1].split(',')[0]:
            sw = True

    if sw:
        print "{0[0]}({0[1]})".format(lines[index].split(','))
    else:
        print lines[index].split(',')[0]

