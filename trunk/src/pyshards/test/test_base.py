# Copyright (C) 2008 Devin Venable 
import unittest
import string, random
from core.sharded_session import ShardedSession
from djangoconf.shard import django_standalone_helper 
from core.loader import DjangoShardLoader
import warnings
import pickle

class TestBase(unittest.TestCase):

    def setUp(self):
        self.shardconf = DjangoShardLoader()
  
    def __randString(self):
        return ''.join([random.choice(string.letters) for x in xrange(10)])
    
    def __makeBogusUserData(self):
        first = self.__randString()
        last = self.__randString()
        return {'first': first,'last': last,'email': '%s@%s.com' % (first, last) }

    def __fillerString(self):
        return ''.join([random.choice(string.letters) for x in xrange(1000)])
   
    def recreateUserTestTables(self):
        warnings.filterwarnings("ignore", "Unknown table.*")
            
        cursor = self.session.adminCursor()
        cursor.executeAll('drop table if exists user_comment')
        cursor.executeAll('drop table if exists user')
        ''' Virtual shards are such a good idea that I almost think they should be 
        required.  But then again, this is Python, so we'll trust the programmer to 
        make the right choice.  Without virtual shards you will not be able to use PyShard
        tools to insert new physical shards and rebalance.
        '''
        cursor.executeAll(''' 
            CREATE TABLE user (
                   id INT NOT NULL AUTO_INCREMENT
                 , VIRTUAL_SHARD INT NULL
                 , userid VARCHAR(50) NOT NULL
                 , firstName VARCHAR(50) NOT NULL
                 , lastName VARCHAR(70) NOT NULL
                 , validated BOOLEAN
                 , suspended BOOLEAN
                 , PRIMARY KEY (id)
            ) ENGINE=InnoDB 
            ''')
        cursor.executeAll(''' 
            CREATE TABLE user_comment (
                   id INT NOT NULL AUTO_INCREMENT
                 , VIRTUAL_SHARD INT NULL
                 , user_id INT NOT NULL
                 , comment TEXT NOT NULL
                 , PRIMARY KEY (id)
                 , INDEX (user_id)
                 , CONSTRAINT FK_user_comment_1 FOREIGN KEY (user_id)
                              REFERENCES user (id)
            ) ENGINE=InnoDB 
            ''')
    
    def loadOrCreateData(self, pickleName):
        dbfile = None 
        try:
            dbfile = open(pickleName, 'r')
            db = pickle.load(dbfile)
            if len(db) > 0:
                dbfile.close()
                return db
        except:
            print "file does not yet exist"
                
        dbfile = open(pickleName, 'w')
            
        self.recreateUserTestTables()
        keepers = [] 
        for i in range(0,10000): 
            
            # insert random user and comment
            user = self.__makeBogusUserData()
            cursor = self.session.insertCursor(user['email'])
            id = cursor.insert('user', '''
                               insert into user (userid, firstName, lastName, validated, suspended )
                               values (%s, %s, %s, 1, 0)
                               ''', (user['email'], user['first'], user['last'] ))
                
            #print 'id of user record is %d' % id
                    
            cursor.insert('user', '''
                          insert into user_comment (user_id, comment)
                          values (%s, %s)
                          ''', (id, self.__fillerString()))
                
            if i % 1000:
                keepers.append(user)
            
        pickle.dump(keepers, dbfile)
        dbfile.close()
        return keepers
