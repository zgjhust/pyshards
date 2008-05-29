# Copyright (C) 2008 Devin Venable 
# Ubuntu users:   sudo apt-get install python-sqlalchemy
import sqlalchemy.pool as pool
import MySQLdb as mysql

mysql = pool.manage(mysql)




