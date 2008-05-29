# Copyright (C) 2008 Devin Venable 
import unittest
import string, random
from djangoconf.shard import django_standalone_helper 
from core.sharded_session import ShardedSession
from core.sharded_session import ShardCursor
from core.loader import DjangoVShardLoader 
from test_base import TestBase 
import timeit

class TestVirtual(TestBase):
    
    def setUp(self):
        TestBase.setUp(self)
        self.session = ShardedSession(self.shardconf, DjangoVShardLoader() )

        # modify configuration: reduce capacity for this test and check often
        for shard in self.session.shards:
            while shard != None:
                shard.capacity_MB = 1
                shard.SIZE_CHECK_INTERVAL = 100
                shard = shard.next

        self.keepers = self.loadOrCreateData('virtual-user-pickle') 
    
    def testJoinQuery(self):
        for k in range(1,10): 
            shardCursor = self.session.cursor(self.keepers[k]['email'])
            res = shardCursor.selectOne("""select * from user u, user_comment uc 
                                           where lastName = '%s' and u.id = uc.user_id
                                        """ % self.keepers[k]['last'])
            print res
            self.assert_(res[3] == self.keepers[k]['first']);

        # selectAll should have same basic result, but result will be tuple in list
        for k in range(10,20): 
            shardCursor = self.session.cursor(self.keepers[k]['email'])
            res = shardCursor.selectAll("""select * from user u, user_comment uc 
                                           where lastName = '%s' and u.id = uc.user_id
                                        """ % self.keepers[k]['last'])
            print res
            # should be one row
            self.assert_(len(res) == 1)
            tup = res[0]
            self.assert_(tup[3] == self.keepers[k]['first']);
        
    def no_testVirtualMappings(self):

        allCursor = self.session.allCursor()
        res = allCursor.countOne("select count(*) from user")        
        
        self.assert_(res == 10000)
       
        for k in self.keepers: 
            shardCursor = self.session.cursor(k['email'])
            res = shardCursor.selectOne("select firstName, lastName from user where lastName = '%s'" % k['last'])
            print res
            self.assert_(len(res) == 2)
            self.assert_(res[0] == k['first']);
        
        #res = allCursor.selectAll('select distinct VIRTUAL_SHARD from user')
        #distinct keyword - yet another concept that does not work across shards
        
        