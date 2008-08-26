# Copyright (C) 2008 Devin Venable 
import MySQLdb  
import pooling

class Shard:
    def __init__(self, id, user, password, host, database, capacity_MB, current_MB, full, observers = None ):
        self.id = id 
        self.user = user
        self.password = password
        self.host = host
        self.database = database 
        self.capacity_MB = capacity_MB
        self.current_MB = current_MB
        self.__full = full
        self.next = None
        self.observers = observers
        # size check is performance overhead, so we only check periodically
        self.sizeCheckCnt = 0
        self.SIZE_CHECK_INTERVAL = 1000
        self.nextInitialized = False

    def setFull(self, full):
        self.__full = full
        if self.observers != None:
            for o in self.observers:
                o.notifyFull(self, full)

    def full(self):
        return self.__full
    
    def getNextForWrite(self):
        if not self.nextInitialized:
            self.__initializeNext()
        return self.next
       
    #This function sets the AUTO_INCREMENT values on tables in the next shard in a bucket.
    
    def __initializeNext(self):
        meta = []
        connection = self.establishConnection()
        cursor = connection.cursor()
        sql = 'show tables'
        cursor.execute(sql)
        tables  = cursor.fetchall()
        for t in tables:
            meta.append({'name': t[0]})
        for t in meta:
            cursor.execute('desc ' + t['name']) 
            cols = cursor.fetchall()
            idfound = False
            for col in cols:
                if col[0] == 'id':
                   idfound = True
            if not idfound:
                meta.remove(t) 
        for t in meta:
            cursor.execute('select max(id) from ' + t['name'])
            one = cursor.fetchone()[0]
            print one
            t['nextid'] = one + 1
        cursor.close()
        connection.close()
        connection = self.next.establishConnection()
        cursor = connection.cursor()
        # TODO: select count from tables, ensure all are zero in length, and raise exception if not
        for t in meta:
            try:
                print 'alter table %s AUTO_INCREMENT = %d' % (t['name'], t['nextid'])
                cursor.execute('alter table %s AUTO_INCREMENT = %d' % (t['name'], t['nextid']))
            except:
                print 'table does not exist in this shard (or other unexpected error)'
        cursor.close()
        connection.close()
        self.nextInitialized = True;
        
    # Creates a connection proxy for this shard from a pool of connections.  
    
    def establishConnection(self, useDB = True):
        connection = None
        if useDB:
            connection = pooling.mysql.connect(host = self.host,
                       user = self.user,
                       passwd = self.password,
                       db = self.database,
                       use_unicode=True)
        else:
            print 'host %s, user %s, pass %s' % (self.host, self.user, self.password)  
            connection = pooling.mysql.connect(host = self.host,
                       user = self.user,
                       passwd = self.password)
        
        if (self.sizeCheckCnt == 0 or self.sizeCheckCnt > self.SIZE_CHECK_INTERVAL):
            self.__checkDBSize(connection)
        else:
            self.sizeCheckCnt = self.sizeCheckCnt + 1
        
        return connection
    
    # This function checks the size of the shard. If the capacity goals have 
    # been met, the shard is flagged as full.  If the shard is full and if
    # a child shard has been specified, new inserts will go into the child shard.
    # If full child is not set, inserts will still be written to this shard to avoid
    # data loss.  The only real harm in writing to a 'full' shard is performance 
    # degredation over time.
    #
    # The size check sql is based on a snippet taken from http://www.markleith.co.uk/?p=7.  
    # Improvements are invited.
    
    def __checkDBSize(self, connection):
        sql = """ 
            SELECT 
            IFNULL(ROUND((SUM(t.data_length)+SUM(t.index_length)) 
            /1024/1024,2),0.00) total_size,
            COUNT(table_name) total_tables
            FROM INFORMATION_SCHEMA.SCHEMATA s
            LEFT JOIN INFORMATION_SCHEMA.TABLES t ON s.schema_name = t.table_schema
            WHERE s.schema_name = %s 
        """ 
        cursor = connection.cursor()
        cursor.execute(sql, self.database)
        result  = cursor.fetchone()
        if result != None:
           size = result[0]
           self.current_MB = size
           if size > self.capacity_MB:
               self.setFull(True)
               #print "Shard configured capacity reached"
           else:
               self.setFull(False)
           if self.observers != None:
               for o in self.observers:
                   o.notifyShardSize(self, size)
        cursor.close ()
