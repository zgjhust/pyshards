# Copyright (C) 2008 Devin Venable 
from pyshards.core.shard import Shard
from pyshards.djangoconf.shard.models import * 
import string


shardConfs = ShardConf.objects.all().order_by('pid');

def XmlShardLoader():
    print 'todo: other ways to store shard configuration like files'
    
def DjangoShardLoader():
    topshards = {}
    bucketshards = {}
    shardConfs = ShardConf.objects.all().order_by('pid');
    for sc in shardConfs:
        #print sc
        sh = Shard(sc.id, sc.user, sc.password, sc.host, sc.database, 
                   sc.capacity_MB, sc.current_MB, sc.full, sc.initialized, (sc,))
        if sc.pid == None:
            topshards[sh.id] = sh
        else:
            if topshards.has_key(sc.pid):
                parShard = topshards[sc.pid]
            else:
                parShard = bucketshards[sc.pid]
            parShard.next = sh
            bucketshards[sh.id] = sh
    
    print "Total shards: %d" % len(topshards.keys())         
    return topshards.values()
        
def DjangoVShardLoader():
    dict = {}
    vshardConfs = VShardConf.objects.all();
    for vs in vshardConfs:
         dict[vs.id] = vs.pid
         #print 'dict[%d] = %d' % (vs.id, vs.pid)
    if len(dict) == 0:
        return None
    print "Total virtual shard ids: %d" % len(dict.keys())         
    return dict

if __name__ == '__main__':
    DjangoShardLoader()