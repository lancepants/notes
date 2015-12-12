.. _cassandra:

Cassandra
=========

Intro
-----

Cassandra uses consistent hashing to distribute data and transfers request and data between nodes directly (peer to peer), much the same way as :ref:`dynamo`. A client may choose, upon each request (SELECT, UPDATE, INSERT, DELETE...), how much consistency they desire (ie: how many nodes to respond before a confirmed operation). Interaction with Cassandra uses *Cassandra Query Language* (CQL), which is nearly identical to SQL. Cassandra allows you to apply replication configurations to each of your databases (ie: keyspaces) which take into account running a keyspace across multiple datacenters and physical racks.

In contrast to Dynamo's preference list, any Cassandra node in a cluster can become coordinator for any read/write request. Similar to Dynamo's "hinted handoff," if one or more nodes responsible for a particular set of data are down, data is simply written to another node which temporarily holds the data until the downed node comes back online.

When data is written to Cassandra, it is first written to a commit log. It is also written to an in-memory structure called a memtable, which is eventually flushed to a disk structure called a *sorted strings table* (sstable). When a read request comes in, it is sent out to the node(s) containing the data, who then perform their work in parallel. If a node is down, the request is forwarded to one of its replicas.

Regarding performance, in 2011 Netflix was able to achieve 3.3million writes per second (1.1million with N=3) across three amazon availability zones using 288 medium size instances (96 instances per AZ). Cassandra is touted to have a linear performance increase as you add more nodes.

With regards to data structure, Cassandra can store structured, semi structured, and unstructured data. In contrast to RDBMS's, you can't do JOINs, so data tends to be pretty denormalized (ie: lots of columns). This is no big deal - Cassandra operates very quickly on objects with many thousands of columns. Within a keyspace are one or more column families, which are like relational tables. These families have one to many thousands of columns, with both primary and secondary indexes on columns being supported. More on this later.

Datastax is the main "enterprise support" for Cassandra company. They employ some Cassandra contributors and have employees who sit on Apache's board.
