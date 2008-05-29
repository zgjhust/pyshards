# Copyright (C) 2008 Devin Venable 
import unittest
import string, random
from djangoconf.shard import django_standalone_helper 
from core.sharded_session import ShardedSession
from core.sharded_session import ShardCursor
from test_base import TestBase 
import timeit

class TestSizeCheck(TestBase):
    
        
    def testExceedSize(self):
        session = ShardedSession(self.shardconf)
        
        # modify configuration: reduce capacity for this test and check often
        for shard in session.shards:
            while shard != None:
                shard.capacity_MB = 1
                shard.SIZE_CHECK_INTERVAL = 100
                shard = shard.next
      
        # will load and insert/distribute data across n shards (n is determined by
        # configuration.  Recommended: 4 Shard buckets with three shards in each)  
        keepers = self.loadOrCreateData('user-pickle') 
        
        allCursor = session.allCursor()
        res = allCursor.countOne("select count(*) from user")        
        
        self.assert_(res == 10000)
        
        shardCursor = session.cursor(keepers[0]['email'])
        res = shardCursor.selectOne("select firstName, lastName from user where lastName = '%s'" % keepers[0]['last'])
        print res
        self.assert_(len(res) == 2)
        self.assert_(res[0] == keepers[0]['first']);

        res = shardCursor.selectMany("select firstName, lastName from user where lastName = %s", keepers[0]['last'], 10)
        print res
        self.assert_(len(res) == 1)
        self.assert_(res[0][0] == keepers[0]['first']);

        res = shardCursor.selectAll("select firstName, lastName from user where lastName = '%s'" % keepers[0]['last'])
        print res
        self.assert_(len(res) == 1)
        self.assert_(res[0][0] == keepers[0]['first']);
        
        res = allCursor.selectOne("select firstName, lastName from user where lastName = '%s'" % keepers[0]['last'])
        print res
        self.assert_(len(res) == 2)
        self.assert_(res[0] == keepers[0]['first']);
        
        res = allCursor.selectMany("select firstName, lastName from user where lastName = %s", keepers[0]['last'], 5)
        print res
        self.assert_(len(res) == 1)
        self.assert_(res[0][0] == keepers[0]['first']);

        res = allCursor.selectAll("select firstName, lastName from user where lastName = '%s'" % keepers[0]['last'])
        print res
        self.assert_(len(res) == 1)
        self.assert_(res[0][0] == keepers[0]['first']);
