#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2020/3/9 8:59 AM
# @Author : mayra.zhao
# @File   : aliyun_api.py

import json
from datetime import date,datetime
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
# from aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest import DescribeInstancesRequest
import aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest

def default(o):
    if type(o) is date or type(o) is datetime:
        return o.isoformat()

class AliyunAPI(object):
    def __init__(self,access,secret,region):
        self.access = access
        self.secret = secret
        self.region = region
        self.client = AcsClient(access, secret, region)
    def get_ecs_expired_time(self):
        self.request = DescribeInstancesRequest()
        self.request.set_accept_format('json')
        self.Instances = json.loads(self.client.do_action_with_exception(self.request))['Instances']['Instance']
        ecs_data = []
        for i in self.Instances:
            chargetype = i['InstanceChargeType']
            if chargetype == 'PrePaid':
                expiredtime = i['ExpiredTime']
            else:
                expiredtime = None
            instanceid = i['InstanceId']
            region = i['RegionId']
            ecs_data.append([chargetype, expiredtime, instanceid, region])
        return ecs_data
    def get_rds_expired_time(self):
        self.request = DescribeDBInstancesRequest()
        self.request.set_accept_format('json')
        self.DBInstances=json.loads(self.client.do_action_with_exception(self.request))['Items']['DBInstance']
        rds_data=[]
        for i in self.DBInstances:
            chargetype=i['PayType']
            if chargetype == 'Prepaid':
                expiredtime = i['ExpireTime']
            else:
                expiredtime = None
            dbinstanceid = i['DBInstanceId']
            region=i['RegionId']
            rds_data.append([chargetype,expiredtime,dbinstanceid,region])
        return rds_data
    def get_redis_expired_time(self):
        self.request = aliyunsdkr_kvstore.request.v20150101.DescribeInstancesRequest.DescribeInstancesRequest()
        self.request.set_accept_format('json')
        self.KVStoreInstances = json.loads(self.client.do_action_with_exception(self.request))['Instances']['KVStoreInstance']
        redis_data=[]
        for i in self.KVStoreInstances:
            chargetype=i['ChargeType']
            expiredtime=i['EndTime']
            kvinstance_id=i['InstanceId']
            region=i['RegionId']
            redis_data.append([chargetype,expiredtime,kvinstance_id,region])
        return redis_data