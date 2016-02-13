### Project Status ###
No longer active.

### Research ###
Pyshards was essentially a personal research project as well as the foundation for a sharding system I developed for a startup company.

### Why did you do this? ###
I had been interested in sharding concepts since first hearing the term "shard" a few years back.  My interest was first piqued when reading about Google's original approach to distributed search, described as a hashtable-like system in which independent physical machines play the role of the buckets.  More recently, I needed the capacity and performance of a Sharded system, but did not find helpful libraries or toolkits which would assist with the configuration for my language of preference these days, which is Python.  And, since I had a few weeks on my hands, I decided to begin the work of creating these tools.

### Inspiration ###
I found a lot of inspiration and good information about sharding on http://highscalability.com. Much has also been written about horizontal partitioning on the MySQL site, where I found articles by Robin Schumacher and a good paper entitled MySQL Scale-Out by application partitioning by Oli Sennhauser.  Another source of information: MySQL Clustering by Alex Davies and Harrison Fisk.  Finally, I drew inspiration from Max Ross' Hibernate Shards project, especially the idea of virtual shards.

### Project Goals ###
  * Provide a sharding library in Python
  * SQL based
    * ORMs are nice, but experienced SQL hackers want to use their power SQL mojo.  As much as possible, this project aspires to allow them to do that.  SQL was designed, however, for use within a single database and as such there are certain constraints that must be imposed in order to construct SQL that makes sense across multiple databases.  This project aspires to keep the constraints to a minimum and as unobtrusive as is possible.
  * Provide out-of-the-box re-balancing (re-sharding) tools
    * Re-balancing is a big deal.  If you don't plan ahead, pain awaits you.  This project will incorporate balance planning into its core design.
  * Monitoring Tools
    * We'd like to see a web-based portal that shows the user the state and capacity of all shards.  We intend to build one.

# Terminology #

As it is early in the lifetime of this project, these terms are subject to change.  If you are purusing the code, it may help to know my definitions for these terms.

| **Term** | **Definition** |
|:---------|:---------------|
| Shard    | A physical shard (a database instance) |
| VShard   | A virtual shard (a mapping mechanism that simplifies re-balancing) |
| Shard Bucket | Linked list of shards in a bucket |
| Shard Head | First Shard in Shard Bucket |
| Inactive Shard | 2nd through last Shard in ShardBucket (ready for use, but has not been activated since its capacity has not been needed) |
| Active Shard | Any physical Shard in use |
| VShard Group | A list of VShards which point to a single physical Shard |


### Why MySQL? ###

MySQL is easy to use and its fast.  I find it easiest to pick a set of technologies and work with them initially rather than putting everything behind generic interfaces.  If we want to add support for other dbs later (postgresql) it will not be difficult.  Injecting interfaces is quite a bit easier to do after the fact in Python than it is in most compiled languages.  Feel strongly that we should use postgresql?  Post a comment and we'll weigh the pros and cons.