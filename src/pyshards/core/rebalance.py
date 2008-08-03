# Copyright (C) 2008 Devin Venable 
import djangoconf.shard.django_standalone_helper
from djangoconf.shard.models import *
from djangoconf.loader import *
from sharded_session import ShardedSession
from shard import Shard

"""The idea is to take a range of virtual shard ids that are mapped to a physical shard, 
divide the range, and move the lower half to the new physical shard.

assumptions: newEmptyShard has an identical schema, VIRTUAL_SHARD column was provided for tables in
toSplitShard and has been correctly populated.
"""
  
def rebalanceShardBucket(toSplitShard, newEmptyShard, virtualRange ):
    
    """This code has not been completed.  However, it does capture the
    algorithm, which was my intent when I sat down to quickly write this 
    up tonight. 
    """
    
    vlength = virtualRange[1] - virtualRange[0]
    print 'length %d' % vlength
    lowRangeTop = vlength/2
    print 'lowRangeTop %d' % lowRangeTop
    moveRange = (virtualRange[0], virtualRange[0] + lowRangeTop - 1)
    print 'moveRange %d,%d' % moveRange
    
    meta = []
    connection = toSplitShard.establishConnection()
    cursor = connection.cursor()
    sql = 'show tables'
    cursor.execute(sql)
    tables  = cursor.fetchall()
    # get table names
    for t in tables:
        meta.append({'name': t[0]})
    # ignore tables without VIRTUAL_SHARD; otherwise remember column names 
    for t in meta:
        cursor.execute('desc ' + t['name']) 
        cols = cursor.fetchall()
        idfound = False
        collist = []
        for col in cols:
            collist.append(col[0])
            if col[0] == 'VIRTUAL_SHARD':
               idfound = True
        if not idfound:
            meta.remove(t)
        else:
            t['cols'] = collist
     # now get the rows to move
    for t in meta:
        cursor.execute('select * from ' + t['name'])
        rows = cursor.fetchall()
        t['rows'] = rows 
    cursor.close()
    connection.close()
    connection = newEmptyShard.establishConnection()
    cursor = connection.cursor()
    for t in meta:
        for row in t['rows']:
            sql =  'insert into %s ('  % t['name']
            sql += ",".join(t['cols'])
            sql += ') values ('
            sql += ",".join( map(str,row) ) 
            sql += ')'
                   
            print sql
            # TODO: insert into second DB, and then remove rows from original
    cursor.close()
    connection.close()
   
   
if __name__ == '__main__':
    shardconf = DjangoShardLoader()
    session = ShardedSession(shardconf)
    
    session.adminCursor().executeAll('delete from throwawayshard.user')
    session.adminCursor().executeAll('delete from throwawayshard.userComment')
    
    sc = ShardConf()
    sc.id = 10000
    sc.capacity_MB = 100
    sc.current_MB = 0
    sc.database = 'throwawayshard'
    sc.full = False
    sc.user = 'root'
    sc.password = 'xx'
    sc.host = '192.168.0.201'
    sc.save()
    
    sh = Shard(sc.id, sc.user, sc.password, sc.host, sc.database, 
                   sc.capacity_MB, sc.full, (sc,))

    rebalanceShardBucket(session.shards[0], sh, (1,19))