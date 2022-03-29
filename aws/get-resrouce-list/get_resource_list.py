#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2019/11/5 11:55 AM
# @Author : mayra.zhao
# @File   : get_resource_list.py
import boto3
import time
from modules.ExcelHandler import *

currDate = time.strftime('%y%m%d-%H%M',time.localtime(time.time()))
reportFile = "SRCN_RI_Resource_List_BJ_{}.xls".format(currDate)

region = 'cn-north-1'
def get_ec2():
    ec2_data = []
    ec2_data.append(
        ['Region', 'Account', 'Instance Name', 'Instance ID', 'Instance Type', 'Platform', 'Image', 'OS', 'State',
         'Env'])
    # projects = ['Account','APPS','AUTH','CIEL','CPM','FKP','IMS','KPI','MAIN','RM','SAS','SA','SSO','FRAME','PROSERVICE']
    projects = ['PROSERVICE']
    for project in projects:
        session = boto3.Session(profile_name=project)
        ec2 = session.resource('ec2',region_name=region)
        for i in ec2.instances.all():
            try:
                instance_name = [t.get('Value') for t in i.tags if t.get('Key') == 'Name'][0]
            except Exception as e:
                instance_name = None

            try:
                instance_env = [t.get('Value') for t in i.tags if t.get('Key') == 'Env'][0]
            except Exception as e:
                instance_env = None
            try:
                os = i.image.name
            except Exception as e:
                os = None
            instance_id = i.id
            instance_type = i.instance_type
            platform = i.platform
            image = i.image_id
            state = i.state.get('Name')
            ec2_data.append([region,project,instance_name,instance_id,instance_type,platform,image,os,state,instance_env])
    return ec2_data

def get_rds():
    rds_data = []
    rds_data.append(
        ['RDS Name', 'RDS Type', 'Status', 'AZ', 'Multi AZ', 'replica', 'Engine Type', 'Engine Version', 'Endpoint',
         'Port', 'Subnet Group', 'Parameter Group', 'Backup Windows', 'Backup Retention', 'Maintenance Window', 'Env',
         'BGC-Monitor', 'BGC-Operation'])
    # projects = ['Account', 'APPS', 'AUTH', 'CIEL', 'CPM', 'FKP', 'IMS', 'KPI', 'MAIN', 'RM', 'SAS', 'SA', 'SSO','FRAME']
    projects = ['PROSERVICE']
    for project in projects:
        session = boto3.Session(profile_name=project)
        rds = session.client('rds', region_name=region)
        response = rds.describe_db_instances()["DBInstances"]
        for db in response:
            try:
                tags = json.dumps(rds.list_tags_for_resource(ResourceName=db['DBInstanceArn'])['TagList'])
            except:
                tags = None
            try:
                env = [t.get('Value') for t in tags if t.get('Key') == 'Env'][0]
            except:
                env = None

            try:
                bgc_monitor = [t.get('Value') for t in i.tags if t.get('Key') == 'BGC-Monitor'][0]
            except Exception as e:
                bgc_monitor = None

            try:
                bgc_ops = [t.get('Value') for t in i.tags if t.get('Key') == 'BGC-Operation'][0]
            except Exception as e:
                bgc_ops = None

            name = db['DBInstanceIdentifier']
            type = db['DBInstanceClass']
            status = db['DBInstanceStatus']
            az = db['AvailabilityZone']
            multiaz = db['MultiAZ']
            replica = db['ReadReplicaDBInstanceIdentifiers']
            engine_type = db['Engine']
            engine_version = db['EngineVersion']
            endpoint = db['Endpoint']['Address']
            port = db['Endpoint']['Port']
            subnetgroup = db['DBSubnetGroup']['DBSubnetGroupName']
            parametergroup = db['DBParameterGroups'][0]['DBParameterGroupName']
            backup_windows = db['PreferredBackupWindow']
            backup_retention = db['BackupRetentionPeriod']
            maintain_windows = db['PreferredMaintenanceWindow']
            # print(json.dumps(db,sort_keys=True,indent=1,default=default))
            rds_data.append(
                [name, type, status, az, multiaz, replica, engine_type, engine_version, endpoint, port, subnetgroup,
                 parametergroup, backup_windows, backup_retention, maintain_windows, env, bgc_monitor, bgc_ops])
    return rds_data

def get_ecc():
    ecc_data = []
    ecc_data.append(
        ['ECC Name', 'CacheNodes Numbers', 'ECC Engine', 'ECC Engine Version', 'CacheNode Type', 'AZ', 'Security Group',
         'Subnet Group Name', 'Maintenance Windows', 'Backup Retention'])
    # projects = ['Account', 'APPS', 'AUTH', 'CIEL', 'CPM', 'FKP', 'IMS', 'KPI', 'MAIN', 'RM', 'SAS', 'SA', 'SSO','FRAME']
    projects = ['PROSERVICE']
    for project in projects:
        session = boto3.Session(profile_name=project)
        ecc = session.client('elasticache',region_name=region)
        response = ecc.describe_cache_clusters()["CacheClusters"]
        # print(json.dumps(response,sort_keys=True,indent=1,default=default))
        for i in response:
            nodes = i["NumCacheNodes"]
            maintenancewindow = i["PreferredMaintenanceWindow"]
            SnapshotRetentionLimit = i["SnapshotRetentionLimit"]
            ECC_Name = i["CacheClusterId"]
            ECC_Engine = i["Engine"]
            ECC_Engine_Version = i["EngineVersion"]
            CacheNodeType = i["CacheNodeType"]
            PreferredAvailabilityZone = i["PreferredAvailabilityZone"]
            SG_ID = i["SecurityGroups"][0]["SecurityGroupId"]
            CacheSubnetGroupName = i["CacheSubnetGroupName"]
            ecc_data.append([ECC_Name, nodes, ECC_Engine, ECC_Engine_Version, CacheNodeType, PreferredAvailabilityZone, SG_ID,CacheSubnetGroupName,maintenancewindow,SnapshotRetentionLimit])
    return ecc_data

if __name__ == '__main__':
    excelHanlder = ExcelHandler(reportFile)
    ec2_data = get_ec2()
    excelHanlder.addSheet('EC2', ec2_data[0])
    for data in ec2_data[1:]:
        excelHanlder.writeToExcel(data)
    rds_data = get_rds()
    excelHanlder.addSheet('RDS', rds_data[0])
    for data in rds_data[1:]:
        excelHanlder.writeToExcel(data)
    ecc_data = get_ecc()
    excelHanlder.addSheet('ECC', ecc_data[0])
    for data in ecc_data[1:]:
        excelHanlder.writeToExcel(data)
