import os
import json
import boto3
import logging
import datetime
from datetime import timezone
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#project
project = "SRCN"
#区域
region = 'cn-north-1'
# Default retention's day is 30.
retention_days = 30
# SNS
TopicArn='arn:aws-cn:sns:cn-north-1:405509095605:srcn-ec2-snapshot'
# Message
file_path='/tmp/snapshot.log'

def logger_message(message,method):
    with open(file_path, method) as f:
        f.write(message)
        f.close()

def backup():
    logger.info("AWS snapshot backups starting at {0}".format(datetime.datetime.now(timezone.utc)))
    logger_message("AWS snapshot backups starting at {0}\n".format(datetime.datetime.now(timezone.utc)),'w')
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    filter_objects = [
        {
            'instance_id': instance.id,
            'instance_name': [
                t.get('Value') for t in instance.tags if t.get('Key') == 'Name'
            ][0]
        } for instance in instances
        if instance.tags
        for tag in instance.tags if tag.get('Key') == 'snapshot' and tag.get('Value') == 'True'
    ]

    logger.debug("Auto Backup servers' list is %s", filter_objects)
    for instance in filter_objects:
        server_name = instance['instance_name']
        Subject = "{} Snapshot 【 {} 】Success".format(project,server_name)
        logger.info("【 {} 】".format(server_name))
        logger_message("\n【 {} 】\n".format(server_name),'a')
        for volume in ec2.volumes.filter(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance['instance_id']]}]):
            description = '{0};{1};{2}'.format(
                instance['instance_name'],
                volume.volume_id,
                datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S"))
            try:
                checks = [
                    snapshot.description for snapshot in volume.snapshots.all() if snapshot.description
                ]
                if description not in checks:
                    # Create new snapshot.
                    snapshot_name = 'Auto_Backup:{0}'.format(instance['instance_name'])
                    if volume.create_snapshot(
                            TagSpecifications=[
                                {
                                    'ResourceType': 'snapshot',
                                    'Tags': [
                                        {
                                            'Key': 'Name',
                                            'Value': snapshot_name
                                        }
                                    ]
                                }
                            ],
                            VolumeId=volume.volume_id,
                            Description=description
                    ):
                        logger.info("【 Created 】Snapshot created with description {0}".format(description))
                        logger_message("【 Created 】Snapshot created with description {0}\n".format(description),'a')
                else:
                    logger.warning("The snapshot does exist,{0}".format(description))
                    logger_message("The snapshot does exist,{0}\n".format(description),'a')
            except Exception as e:
                logger.error("【 Created 】create the snapshot error {0}".format(e))
                Subject = "{} Snapshot【{}】 Failed".format(project,server_name)
                pass
            delete_expired_snapshot(volume)
        logger.info("【Finished】AWS Snapshot backups completed at region:{0}; {1}".format(region, datetime.datetime.now()))
        logger_message("【Finished】AWS Snapshot backups completed at region:{0}; {1}\n".format(region, datetime.datetime.now()),'a')
        with open(file_path, 'r') as f:
            message = f.read()
            f.close()
        sns_publish(TopicArn,Subject,message)
        
        with open(file_path,'r+') as f:
            f.truncate()
            f.close()
    return True

def delete_expired_snapshot(volume):
    # Delete over-expored snapshots.
    try:
        for snapshot in volume.snapshots.all():
            now_time = datetime.datetime.now(timezone.utc)
            time_checking = (now_time - snapshot.start_time.replace(tzinfo=timezone.utc) > datetime.timedelta(
                days=retention_days))
            if (
                    snapshot.tags and
                    time_checking and
                    [
                        t.get('Value') for t in snapshot.tags
                        if t.get('Key') == 'Name' and t.get('Value').startswith('Auto_Backup')
                    ]
            ):
                logger.info('Deleting snapshot [{0} - {1}]'.format(snapshot.snapshot_id, snapshot.description))
                logger_message('Deleting snapshot [{0} - {1}]'.format(snapshot.snapshot_id, snapshot.description),'a')
                snapshot.delete()
    except Exception as e:
        logger.error("【Deleted】Delete the snapshot error {0}:".format(e))
        logger_message("【Deleted】Delete the snapshot error {0}:".format(e),'w')
        pass

def sns_publish(TopicArn,Subject,message):
    sns = boto3.client('sns')
    try:
        response = sns.publish(
            TopicArn=TopicArn,
            Subject=Subject,
            Message=message
        )
        if not isinstance(response, dict):
            logger.error('%s,%s' % (topic_arn, response))
        else:
            logger.info(response['ResponseMetadata'])
    except Exception as  e:
        logger.error(e.message + ' Aborting...')

def lambda_handler(event=None, context=None):
    try:
        backup()
    except Exception as e:
        message = "Failed\n{}\t Aborting...".format(e)
        Subject = "{} Backup script execution Failed".format(project)
        sns_publish(TopicArn,Subject,message)