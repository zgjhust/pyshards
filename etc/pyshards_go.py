import pyshards

from pyshards.djangoconf.loader import DjangoShardLoader
from pyshards.djangoconf.loader import DjangoVShardLoader
from pyshards.core.sharded_session import ShardedSession

session = ShardedSession(DjangoShardLoader(), DjangoVShardLoader())
admin = session.adminCursor() # insert all
all = session.allCursor()     # query all

results = all.selectAll("select count(*) from bigindex")
print 'Total records in index: %d' % sum([ res[0] for res in results])
