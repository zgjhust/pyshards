# Copyright (C) 2008 Devin Venable 
import django_standalone_helper
from djangoconf.shard.models import *
from djangoconf.loader import *
from core.sharded_session import *

def createTestShards(IPs, username, password):
    #Warning: This deletes existing shards
    ShardConf.objects.all().delete()
    shardId = 0
    for ip in IPs:
        pid = None
        for x in range(1,4):
            s = ShardConf()
            s.id = shardId = shardId + 1
            s.capacity_MB = 100
            s.current_MB = 0
            s.database = 'testshard%d' % x
            s.full = False
            s.user = username 
            s.password = password 
            s.host = ip
            if pid != None:
                s.pid = pid
            s.save()
            pid = s.id
            
def createTestSchemas():
        shardconf = DjangoShardLoader()
        session = ShardedSession(shardconf)
        cursor = session.adminCursor()
        cursor.executeAll("drop database testshard1", None , False)
        cursor.executeAll("drop database testshard2", None , False)
        cursor.executeAll("drop database testshard3", None , False)
        cursor.executeAll("drop database testshard4", None , False)
        cursor.executeAll("create database testshard1", None , False)
        cursor.executeAll("create database testshard2", None , False)
        cursor.executeAll("create database testshard3", None , False)
        cursor.executeAll("create database testshard4", None , False)
                
def createVirtualShards(numOfVShards):
    #Warning: This deletes existing virtual shards
    VShardConf.objects.all().delete()
     
    # Assign to Shard Heads only
    pshards = ShardConf.objects.filter(pid__isnull=True)
    numOfShards = len(pshards)
    vPerShard = numOfVShards/numOfShards
    # make zero indexed
    vPerShard = vPerShard - 1
    vShardId = 0
    for sh in pshards:
        for x in range(0, vPerShard):
            v = VShardConf()
            v.id = vShardId = vShardId + 1
            v.pid = sh.id
            v.save()

def demoSetup():
    ips = ('192.168.0.201',
           '192.168.0.206',
           '192.168.0.207')
    createTestShards( ips, 'root', 'xx' )
    createTestSchemas()
    createVirtualShards(100)
            
if __name__ == '__main__':
    demoSetup()