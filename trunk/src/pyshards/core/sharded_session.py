# Copyright (C) 2008 Devin Venable 
import MySQLdb
from cursor import * 

class ShardedSession:
    
    def __init__(self, shards, vshards = None):
        self.shards = shards
        self.vshards = vshards
        self.shardsMap = {}
        for s in self.shards:
            self.shardsMap[s.id] = s 
            
    def cursor(self, shardkey):
        return ShardCursor(self, shardkey) 

    def insertCursor(self, shardkey):
        return ShardInsertCursor(self, shardkey) 

    def adminCursor(self):
        return AdminCursor(self) 

    def allCursor(self):
        return AllCursor(self) 
                             
    def getShardForInsert(self, shardkey):
        return self.getShardByKey(shardkey, True)
    
    def getShardForQuery(self, shardkey):
        return self.getShardByKey(shardkey, False)
        
    def getShardByKey(self, shardkey, insertOper):
        idx = 0
        shard = None
        
        if self.vshards != None:
            idx = shardkey.__hash__() % len(self.vshards) + 1
            print 'idx %d' % idx
            vshardval = self.vshards[idx]
            print "vshardval %d" % vshardval 
            shard = self.shardsMap[vshardval]
        else:
            idx = shardkey.__hash__() % len(self.shards)
            shard = self.shards[idx]
           
        if insertOper: 
            if shard.full() and shard.next == None:
                print "Warning! Full Shard. Add child shard to shard id %s" % shard.id
    
            while shard.full() and shard.next != None:
                shard = shard.getNextForWrite()
                    
        print 'shard bucket #%d, shard IP (%s), shard ID (%d), shard DB (%s)' % (idx, 
                                                                  shard.host,
                                                                  shard.id,
                                                                  shard.database)
        return shard, idx 
            
        
    def close(self):
        raise NotImplementedError 
        
        
        