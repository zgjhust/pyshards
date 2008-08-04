# Copyright (C) 2008 Devin Venable 
import unittest
import MySQLdb

class TestBasicConnection(unittest.TestCase):
    
    #Just making sure the connection pool works and we have basic connectivity
    
    def test_connection(self):
        self.__repeatConnectionSeq()
        self.__repeatConnectionSeq()
        self.__repeatConnectionSeq()
        
    def __repeatConnectionSeq(self): 
        
        conn = MySQLdb.connect (host = '192.168.0.206',
                   user = 'root',
                   passwd = 'xx',
                   db = 'testshard1')
        
        cur = conn.cursor()
        cur.execute('insert into user (userid, firstName, lastName) values ("test","test","test")')
        cur.execute('insert into user (userid, firstName, lastName) values ("test","two","two")')
        cur.execute('select * from user')
        res = cur.fetchall()
        self.assert_(len(res) > 2)
        cur.close()
        conn.commit()
        conn.close()
        