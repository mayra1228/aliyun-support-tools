#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2019/9/25 7:05 PM
# @Author : mayra.zhao
# @File   : get_cdn_logs.py

"""
* 最多拉取40天的日志
"""
import os
import json
import argparse
import subprocess
from datetime import datetime, date, time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcdn.request.v20180510.DescribeCdnDomainLogsRequest import DescribeCdnDomainLogsRequest

parser = argparse.ArgumentParser()
parser.add_argument("--domain", required=True,help="Please input the domain name,such as www.example.cn")
parser.add_argument("--start",required=True, help="Please input the start time(UTC), the format must be %Y-%m-%d %H:%M:%S")
parser.add_argument("--end",required=True,help="Please input the end time (UTC), the format is %Y-%m-%d %H:%M:%S")
parser.add_argument("--access",required=True, help="Please input the access key")
parser.add_argument("--secure",required=True, help="Please input the secure key")

args = parser.parse_args()
start = args.start
end = args.end
access = args.access
secure = args.secure
domain = args.domain
default_region = 'cn-hangzhou'

timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

pathfile = 'cdn_pathfile_{}.log'.format(timestamp)
mergefile = 'cdn_merge_{}.log'.format(timestamp)
logdir = 'log_{}'.format(timestamp)

iso_start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S").isoformat() +'Z'
iso_end = datetime.strptime(end,"%Y-%m-%d %H:%M:%S").isoformat() +'Z'

PIPE = subprocess.PIPE

def get_cdn_logpath():
    client = AcsClient(access, secure, default_region)
    request = DescribeCdnDomainLogsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    request.set_StartTime(iso_start)
    request.set_EndTime(iso_end)
    request.set_PageSize(1000)
    response = json.loads(client.do_action_with_exception(request))
    details = response['DomainLogDetails']['DomainLogDetail'][0]['LogInfos']['LogInfoDetail']
    result= dict()
    for log in details:
        with open(pathfile, 'a+') as f:
            logpath = log['LogPath']
            logname = log['LogName']
            result[logname] = logpath
            f.write(logname + "\t" + logpath)
            f.write('\n')
    return result

def merge_file(source):
    curpath = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(curpath,logdir)
    gunzip = 'find "%s" -name "*.gz" -exec gunzip {} \;' % path
    print("Staring to unzip the logs.....")
    p = subprocess.Popen(gunzip, stdout=PIPE, stderr=PIPE, shell=True)
    # Wait until completion of the process
    while p.returncode == None:
        p.poll()
    # Get the output of executing command
    print(p.returncode)
    if p.returncode != 0:
        print(p.stderr.read())
        print("Logs uncompress failed...")
    else:
        print("Starting to merge files......")
        k = open(source,'a+')
        for file in os.listdir(path):
            print(file)
            with open(os.path.join(path,file),'r') as f:
                content = f.read()
                k.write(content)
        k.close()
        print("The logs has been merged to {}".format(mergefile))

def download_logs(urllist):
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    for logname, logpath in urllist.items():
        command = 'wget "{}" -O {}/{}'.format(logpath,logdir,logname)
        print(command)
        p = subprocess.Popen(command, stdout=PIPE,stderr=PIPE,shell=True)
        # Wait until completion of the process
        while p.returncode == None:
            p.poll()
        if p.returncode != 0:
            print("Download log {} failed, the logpassh is {}".format(logname,logpath))

if __name__ == '__main__' :
    print("Starting to get the logpath from Aliyun CDN......")
    urllist = get_cdn_logpath()
    print("The url list has been saved on {}".format(pathfile))
    print("Starting to download the logs and save as {}....".format(logdir))
    download_logs(urllist)
    print("Downlaod has been finished. ")
    merge_file(mergefile)
