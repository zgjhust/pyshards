# Copyright (C) 2008 Devin Venable 
import MySQLdb
from sets import Set

class BaseCursor:
    
    """ Common cursor functionality
    """
    
    def __init__(self, session):
        self.session = session

    def _execute(self, shard, sql, args, insert = False, useDB = True, tableName = "", vIndex = 0):
        insertid = 0
        db = shard.establishConnection(useDB)
        cursor = db.cursor()
        cursor.execute(sql, args)
        if insert:
            insertid = db.insert_id()
            if vIndex > 0:
                cursor.execute('update %s set VIRTUAL_SHARD = %d where id = %d' % 
                               (tableName, vIndex, insertid) )
                #print 'setting virtual shard to %d' % vIndex
        cursor.close ()
        db.commit()
        db.close ()
        if insert:
            return insertid
    
class AdminCursor(BaseCursor):
    
    """ A class designed for administrative use. It provides methods for executing commands against 
    all shards. This is useful for database setup activities 
    like creating or dropping tables.
    """

    def __init__(self, session):
        BaseCursor.__init__(self, session)
    
    # Execute against all active shards        
    def executeAllActive(self, sql, args=None):
        for shard in self.session.shards:
            self._execute(shard, sql, args)
    
    # Execute against all active and inactive shards        
    def executeAll(self, sql, args=None, useDB=True):
        uniqueHosts = Set([])
        for shard in self.session.shards:
            while shard != None:
                if useDB == False: 
                    if shard.host not in uniqueHosts:
                        uniqueHosts.add(shard.host)
                    else:
                        shard = shard.next
                        continue
                
                self._execute(shard, sql, args, False, useDB)
                
                """
                 
                except:
                    '''
                    This is here because of Unknown table warnings (exceptions) that are raised
                    when "drop table if exists" type queries are executed.  Others have reported
                    this strange behavior and some have said the problem can be avoided by filtering
                    out the warning (see below).  I had no such luck.  For now, this is unresolved 
                    and remains a TODO. 
                    warnings.filterwarnings("ignore", "Unknown table.*")
                    '''
                    print 'TODO - fix or find better workaround for "unknown table" issue in MySQLdb'
                    print 'unknown exception during execute'
                """

                shard = shard.next
                
class ShardInsertCursor(BaseCursor):

    """ ShardInsertCursor should be used for all insert operations.  Operations on this cursor
    will all be written to the same physical database regardless of capacity configuration, so
    don't hang on to it for an extended period of time. Update and Delete operations should be
    used only to update or delete a row just added with this cursor (i.e. following an insert).
    """ 

    def __init__(self, session, shardkey):
        BaseCursor.__init__(self, session)
        self._shard, self._idx = session.getShardForInsert(shardkey)

    def insert(self, tableName, sql, args=None):
        return self._execute(self._shard, sql, args, True, True, tableName, self._idx)

    def update(self, query, args=None):
        return self._execute(self._shard, sql, args)

    def delete(self, query, args=None):
        return self._execute(self._shard, sql, args)
    
    def close(self):
        []
    
class ShardCursor(BaseCursor):

    """ ShardCursor should be used for general read, update and delete operations.
    """
    
    def __init__(self, session, shardkey):
        BaseCursor.__init__(self, session)
        
        # allows construction of class using explicit virtual shard id
        if isinstance(shardkey,int):
            self._shard = session.getShardByVirtualId(shardkey)
            self._idx = shardkey
        else:
            self._shard, self._idx = session.getShardForQuery(shardkey)
        
    def insert(self, sql, args=None):
        #Should never be implemented
        raise NotImplementedError 
        
    def update(self, query, args=None):
        #TODO: we don't know which shard in bucket has the record to
        #update, so we just try updating all and catching exceptions.
        #We need a better strategy for this one.
        shard = self._shard;
        while shard != None and len(results) == 0:
            db = shard.establishConnection()
            cursor = db.cursor()
            try:
                cursor.execute(sql, args)
            except:
                print 'nothing to update here'
                
    def delete(self, sql, args=None):
        #TODO
        raise NotImplementedError 

    def selectOne(self, sql, args=None):
        results = []
        shard = self._shard;
        while shard != None and len(results) == 0:
            db = shard.establishConnection()
            cursor = db.cursor()
            cursor.execute(sql, args)
            res = cursor.fetchone()
            if res != None:
                results.extend(res)
            cursor.close ()
            db.close ()
            shard = shard.next
        return results
    
    def selectMany(self, sql, args=None, size=None):
        results = []
        stillToFetch = size
        shard = self._shard;
        while shard != None and stillToFetch > 0:
            db = shard.establishConnection()
            cursor = db.cursor()
            cursor.execute(sql, args)
            res = cursor.fetchmany(stillToFetch)
            if res != None:
                results.extend(res)
                stillToFetch = stillToFetch - len(res)
            cursor.close ()
            db.close ()
            shard = shard.next
        return results

    def selectAll(self, sql, args=None):
        results = []
        shard = self._shard;
        while shard != None:
            db = shard.establishConnection()
            cursor = db.cursor()
            cursor.execute(sql, args)
            res = cursor.fetchall()
            if res != None:
                results.extend(res)
            cursor.close ()
            db.close ()
            shard = shard.next
        return results

    # Use with 'select count(*)' style queries  
    def countOne(self, sql, args=None):
        total = 0
        shard = self._shard;
        while shard != None:
            db = shard.establishConnection()
            cursor = db.cursor()
            cursor.execute(sql)
            res = cursor.fetchone()
            if res != None:
                total = total + res[0]
            cursor.close ()
            db.close ()
            shard = shard.next
        return total
  
      
class AllCursor(ShardCursor):

    def __init__(self, session):
        # Note that we do not initialize the ShardCursor base, as we intend to 
        # explicitly set shards rather than hash for them when using this cursor.
        BaseCursor.__init__(self, session)
        
    def selectOne(self, sql, args=None):
        results = []
        for shard in self.session.shards:
            self._shard = shard
            res = ShardCursor.selectOne(self, sql, args) 
            if len(res) > 0:
                results.extend(res)
                break
        return results
    
    def selectMany(self, sql, args=None, size=None):
        results = []
        for shard in self.session.shards:
            self._shard = shard
            res = ShardCursor.selectMany(self, sql, args, size) 
            if len(res) > 0:
                results.extend(res)
            if len(results) >= size:
                break
                #TODO: trim to actual size specified?
        return results

    def selectAll(self, sql, args=None):
        results = []
        for shard in self.session.shards:
            self._shard = shard
            res = ShardCursor.selectAll(self, sql, args) 
            if len(res) > 0:
                results.extend(res)
        return results
    
    # Use with 'select count(*)' style queries  
    def countOne(self, sql, args=None):
        total = 0 
        for shard in self.session.shards:
            self._shard = shard
            res = ShardCursor.countOne(self, sql, args) 
            if res != None:
                total = total + res
        return total

    