### Get the source ###

A general release is not yet available.  Checkout from svn.

```
svn checkout http://pyshards.googlecode.com/svn/trunk/ pyshards-read-only
```

### Install needed libraries ###

Ubuntu/Debian users may use this script:

```
#!/bin/bash

apt-get install mysql-server python-mysqldb python-django python-unit python-setuptools python-sqlalchemy
```

Django is not strictly required, however, it is currently being used to store configuration information and alternative methods for storing this info has not been written.  The monitoring application will be based on the Django application, so it may be a firm requirement in the future.

python-sqlalchemy is used for connection pooling.

### Create shardconf database ###

  1. Connect to MySQL using password you specified during installation.
  1. mysql> create database shardconf;

### Set up Django ###

Run syncdb to install the database tables.  When prompted, provide
authentication information to be used by the administrative application. (Create user,
password, etc.)

```
cd pyshards-read-only/src/pyshards/djangoconf/
python manage.py syncdb
```

Start the Django test server.

```
python manage.py runserver
```


Open a web browser and navigate to http://localhost:8000/admin/.  You should see the Django Site administration user interface and a few tables named Shard and VShard.  At this point you would normally need to figure out how many servers you will have available to act as physical shards, create the databases on each machine, and specify configuration parameters.  Then you would decide the total number of shards you will EVER need, and use that information to create VShard records.

There are a few utilities to assist with this job.  But first, lets review the goals of your system.  You want both scalability and performance, right? The main bottlenecks to performance in this kind of system are network (latency and bandwidth) and disk access.  You'll want your servers to be connected on a LAN via a Gigabit (or better) router.  The big problem that we're hoping to duck by Sharding in the first place is the disk access problem. First off, stripe a few drives using RAID0 if you have the option. Now you will want to size your shard to fit into available RAM on each machine.  Once your OS is loaded and running any software that will be running during normal operation, use the "free" command (or something similar) to determine your available memory in MB.  Write down this number.  When configuring a shard for this device, you'll want to set the CAPACITY\_MB attribute to a number below the total available RAM.  I'd recommend 60%-80% of available RAM.  The goal is to keep the DB in memory so that the device NEVER hits swap space.

Back to the tool: There is a utility that will create a series of test databases for initial testing based on a list of IP addresses that you provide.

Navigate to the file and open it.

```
vim pyshards-read-only/src/pyshards/djangoconf/shard/utility.py
```

Note the section at the bottom:

```
if __name__ == '__main__': 
    ips = ('192.168.0.201', 
           '192.168.0.204', 
           '192.168.0.205', 
           '192.168.0.206', 
           '192.168.0.207') 
    createTestShards( ips, 'root', 'xx' )       
    createTestDBs() 
    createVirtualShards(100) 
```

You will need to provide one or more of your own server IP address to createTestShards.  Each box will need to have MySQL server installed.  Change the user and password to whatever credentials you use will be using to connect to these databases remotely.  Change the number of virtual shards if you like to a number greater than the number\_of\_IPs x 4. This script will create four shards per machine.  Is this an ideal configuration?  Probably not, but it simplifies testing.  Modify the script in any way you see fit to optimize for your environment.  Also note the warnings.  This script will blow away any previously saved shard and virtual shard configuration, so use it once and, if your results are good, then think twice before running it ever again.

Note that if you use pydev and eclipse, project files will be included with the checkout and you may run this script from within the IDE.  Otherwise, you'll need to add the project to the syspath.  Run the python interpreter and type the following.

```
>>> import sys
>>> sys.path.append("/your_path_to_checkout_dir/pyshards-read-only/src/pyshards")
>>> from djangoconf.shard.utility import demoSetup
>>> demoSetup()
```

If all went well your system will now be configured for use and you should be able to run the unit test programs.  As a sanity check, open a browser and make sure that you see something similar to the following.

[![](http://farm3.static.flickr.com/2378/2534377509_d4f60d9c4c_o.png)](http://www.flickr.com/photos/27165790@N06/2534377509/)


At this point we're ready to test.  A few unit tests have been started and can be found under the test directory.  These are functional tests really, but I'm using the pyunit framework nonetheless.  I do throw in a few asserts just to confirm that all is proceeding according to plan.

The tests currently use a common base class which creates a number of user records (10,000 currently) and user comments.  The user's email is used as the shard key and all insert fields are randomly generated.  After the initial inserts, a subset of the inserted rows are stored off in a pickle for subsequent runs.  The presence of the file tells the program to to re-run the tests without re-inserting rows, which is a time consuming process.

The first time you run either test\_sizecheck.py or test\_virtual.py, you'll see a lot of print lines describing which virtual shard and shard was used for each insert.  You may also watch the djangoconf webapp (refresh often) to see the databases fill with data.


> _The django webapp imports the pyshards library, so you'll need to have it on your python   path.  For my convenience, I created a symbolic link to my working pyshards root directory from /usr/lib/python2.5/site-packages/ to make the lib accessible to the webapp and the command line interpreter._




More info may be added later, depending on community interest.