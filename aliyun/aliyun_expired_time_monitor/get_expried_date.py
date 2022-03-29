#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2020/3/8 10:58 PM
# @Author : mayra.zhao
# @File   : get_expried_date.py

import os
import sys
import json
import time
import requests
from modules.aliyun_api import AliyunAPI
from datetime import date, datetime, timedelta

#默认阈值为30天
threshold = 2592000
endpoint = ''
config=os.path.join(os.getcwd(), '.aliyun_credentials')
regions=['cn-shanghai','cn-qingdao','cn-beijing','cn-chengdu','cn-zhangjiakou','cn-huhehaote','cn-hangzhou','cn-shenzhen']

def if_expire_within_threshold(expired_time):
    seconds = (expired_time - datetime.now()).total_seconds()
    if seconds > threshold:
        value = 0
    else:
        value = 1
    return value

def send_data(metric,value,tag,step=86400):
    url = "http://127.0.0.1:1988/v1/push"
    str_time = "2020-03-12 11:00:00"
    time_array = time.strptime(str_time,"%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(time_array))
    #ts = int(time.time())
    payload = [
        {
            "endpoint": endpoint,
            "metric": metric,
            "timestamp": ts,
            "step": step,
            "value": value,
            "counterType": "GAUGE",
            "tags": "ac={},reg={},id={}".format(tag[0], tag[2],tag[1]),
        },
    ]
    try:
        response = requests.post(url, data=json.dumps(payload))
        print(response.text)
    except Exception as e:
        print("openfalcon: Error to push data to agent")
        sys.exit(1)

if __name__ == '__main__':
    with open(config,'r') as f:
        credentials = json.load(f)
    for project, cred in credentials.items():
        accessKeyId=cred['accessKeyId']
        accessSecret=cred['accessSecret']
        for region in regions:
            aliyun_api = AliyunAPI(accessKeyId,accessSecret,region)

            ##  Checking ECS Expired Time
            ecs_data = aliyun_api.get_ecs_expired_time()
            for i in ecs_data:
                ecs_metric='ali.ReservedECS.check.expired'
                if i[1]:
                    expired_time = datetime.strptime(i[1], '%Y-%m-%dT%H:%MZ').replace(tzinfo=None)
                    value=if_expire_within_threshold(expired_time)
                    tag=[project,i[2],i[3]]
                    send_data(ecs_metric,value,tag)

            ##  Checking RDS Expired Time
            rds_data = aliyun_api.get_rds_expired_time()
            for i in rds_data:
                rds_metric='ali.ReservedRDS.check.expired'
                if i[1]:
                    expired_time = datetime.strptime(i[1], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=None)
                    value=if_expire_within_threshold(expired_time)
                    tag=[project,i[2],i[3]]
                    send_data(rds_metric,value,tag)

            ## Checking Redis Expired Time
            redis_data = aliyun_api.get_redis_expired_time()
            for i in redis_data:
                redis_metric='ali.ReservedRedis.check.expired'
                if i[1]:
                    expired_time = datetime.strptime(i[1], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=None)
                    value = if_expire_within_threshold(expired_time)
                    tag = [project, i[2], i[3]]
                    send_data(rds_metric, value, tag)
