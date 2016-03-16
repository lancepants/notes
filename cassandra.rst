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


Data Model
----------
A table in Cassandra is a distributed multi dimensional map, indexed by a key. The value is an object which is highly structured. The row key in a table is a string with no size restrictions, although typically 16 to 36 bytes long. Every operation under a single row key is atomic per replica no matter how many columns are being read or written into.

Columns are grouped together into sets called column families very similar to what happens in BigTable. Cassandra exposes two kinds of column families, Simple and Super column families. Super column families can be visualized as a column family within a column family. Furthermore, applications can specify the sort order of columns within a super column or simple column, sorted either by time or by name. Time sorting is good for things like inbox search, where results are always in time sorted order.

Any column within a column family is accessed using the convention *column_family : column* and any column within a column family that is of type super is accessed using the convention *column_family : super_column : column*. More on this later.

Typically, applications use a dedicated Cassandra cluster and manage them as part of their service. Although the system supports the notion of multiple tables, all deployments (at facebook) have only one table in their schema. In other deployments, users may have multiple tables which are each designed to be efficient in serving certain types of queries (eg: grouping by an attribute, ordering by an attribute, filtering based on some set of conditions...etc). Using separate tables and (most likely necessarily) having duplicate copies of data between them (but with different column layouts) is necessary and recommended in order to gain maximum read optimization. In short, design your tables around what high-level queries you have.

API
---
The Cassandra API consists of the following three simple methods:

* *insert(table, key, rowMutation)*
* *get(table, key, columnName)*
* *delete(table, key, columnName)*

*columnName* can refer to a specific column within a column family, a column family, a super column family, or a column within a super column.

System Architecture
-------------------

General
^^^^^^^
Typically a read/write request for a key gets routed to any node in the cluster. The node then determines the replicas for this particular key. For writes, the system routes the requests to the replicas and waits for a quorum of replicas to acknowledge the completion of writes. For reads, based on the consistency guarantees required by the client, the system either routes the requests to the closest replica or routes the requests to all replicas and waits for a quorum of responses.

Partitioning
^^^^^^^^^^^^
Much like Dynamo, Cassandra partitions data across the cluster using consistent hashing - but uses an order preserving hash function to do so (TODO: how does this order preserving hash function affect key placement? what are they talking about here?).

*Basic consistent hashing:* In consistent hashing, the output *range* of a hash function is treated as a fixed circular space or "ring" (ie: the largest hash value wraps around to the smallest hash value). Each node in this system is assigned a random value within this sapcve which represents its position on the ring. Each data item identified by a key is assigned to a node by hashing the key of the data item, getting that value, and then walking the ring from that value clockwise until it hits the first node with a position larger than the item's position. That node then becomes coordinator for that piece of data. So, each node when walking clockwise on the ring is responsible for the range between itself and its predecessor node. The advantage of this system is that when a node is added or removed (and gets a new position on the ring or is removed from its position), it only affects two neighbouring nodes.

Disadvantages of this method include the random-node-position-assignment and the system being oblivious to node hardware differences. The random node assignment around the ring leads to some nodes being responsible for larger keyspaces than others, leading to uneven load distribution. The lack of heterogenity awareness leads to some higher powered nodes not taking on larger key ranges and load than lower power nodes.

To get around this problem, you could assign the same node to multiple positions along the ring, and/or you can analyze the load along the ring and move lightly loaded nodes into keyspace owned by heavily loaded nodes in order to distribute work more efficiently. Both of these approaches incorporate the usage of virtual nodes, or *tokens*, which sit in positions along the ring in place of actual physical nodes. Physical nodes can then be assigned or removed more or less tokens.

.. image:: media/cassandra-tokenarch.png
   :alt: Single vs Virtual token architecture
   :align: center

   **Figure 1: Single token vs Virtual token node assignment**


Replication
^^^^^^^^^^^
As with Dynamo, each data item (ie: **row**) is replicated to N hosts where N is a given replication factor. Each key is assigned to a coordinator node and that coordinator node is responsible for replicating these keys to N-1 other nodes in the ring.

Cassandra provides the client with various options for how data needs to be replicated, such as "Rack Unaware", "Rack Aware (within a datacenter)" and "Datacenter Aware." If a client chooses rack unaware, the data is simply replicated to the next N-1 successors of the coordinator on the ring.

For *rack aware* and *datacenter aware* the system is a bit more complicated. Cassandra first elects a leader amongst its nodes and stores that info in zookeeper. All nodes upon joining a cluster read zookeeper and then contact the leader, who tells them for what ranges they are replicas for. The leader makes a best effort to ensure that no node is responsible for more than N-1 ranges in the ring. The metadata about the ranges a node is responsible for is cached locally at each node as well as in your zookeeper cluster. As such, a node can crash and lose its disk, and still come back up and know what it is responsible for. Cassandra borrows the *preference list* parlance from Dynamo by calling the nodes that are responsible for a given range the *preference list* for that range.

Cassandra is configured to replicate each *row*. It can be configured such that each *row* is replicated across multiple data centers. In this configuration, the preference list for a given key is constructed such that the member storage nodes are spread across multiple datacenters.


Cluster Membership
^^^^^^^^^^^^^^^^^^
Cluster membership in Cassandra is based off of Scuttlebutt, an efficient anti-entropy gossip based algorithm. This gossip based system is used for membership as well as other system related control state data.

TODO: More about scuttlebutt


Failure Detection
^^^^^^^^^^^^^^^^^
Φ aka PHI
A modified version of ΦAccrual Failure Detector is used by each node to determine whether any other node in the system is up or down. The idea of an Accrual Failure Detector is that you are not working with a boolean stating whether a node is up or down. Instead, the value is more of a sliding scale or a "suspicion level." This value is defined as Φ, and its value can be dynamically adjusted to reflect network and load conditions at the monitored nodes.

Φ has the following meaning: given some threshold Φ, and assuming that we decide to "suspect" that node A is down when Φ = 1, then the likelihood that we will make a mistake (ie: the decision will be contradicted in the future by the reception of a late heartbeat) is about 10%. When Φ = 2 that chance of error decreases to 1%, and when Φ = 3 the chance further decreases to 0.1%, and so on.

Every node in the system maintains a sliding window of inter-arrival times of gossip messages from other nodes in the cluster. The distribution of these inter-arrival times is determined and Φ is calculated. In general, accrual failure detectors have been found to be very good in both their accuracy, speed, and in their ability to adjust well to network conditions and server load conditions.

Facebook found that a slightly conservative PHI value of 5 was able to detect failures in a 100 node cluster on average in about 15 seconds.


Bootstrapping
^^^^^^^^^^^^^
When a node starts for the first time, it chooses a random token for its position in the ring (this contradicts other stated info: "when a new node is added to the system, it gets assigned a token such that it can alleviate a heavily loaded node"). For fault tolerance, this position is saved both locally to disk and also to zookeeper. This info is then gossip'd around the cluster, which is how each node knows about all other nodes and their respective positions in the ring. When a node is bootstrapped for the first time, it reads its config (or zookeeper) for a listing of seed nodes - initial contact points to gain information of the cluster from.

TODO: Does the initial gossip advertisement require knowing about one or more seed nodes (likely answered after reading more about scuttlebutt)?


Scaling
^^^^^^^
When a new node is added to the system, it gets assigned a token such that it can alleviate a heavily loaded node (note: contradicts "randomly selected" info above...). This results in the new node splitting a range off the heavily loaded node for itself. The node giving up the data will stream data over to the new node using kernel-kernel copy techniques (TODO: expand). The Cassandra bootstrap algorithm can be initiated by any other node in the cluster, either via command line utility or Cassandra web dashboard.

Operational experience at facebook has shown that data can be transferred at a rate of 40MB/sec from a single node. They are currently working on improving this transfer rate by having multiple replicas take part in the bootstrap transfer, thereby parallelizing the effort, using a method similar to bittorrent.


Local Persistence
^^^^^^^^^^^^^^^^^
Cassandra saves data to disk using a format that lends itself well to efficient data retrieval. A typical write operation involes a write into a commit log, after which (if a successful write to commit log occurs) an update into an in-memory data structure occurs. Facebook uses a dedicated LUN/disk for their commit log. Writes to the commit log are sequential. 

As for the in-memory data structure, once it crosses a certain threshold (calculated based on data size and number of objects) it dumps itself to disk. Along with each data structure, an index is generated which allows efficient lookups on the associated data structure based on row key. Over time, you end up with a lot of files. As such, a background merge process will occaisionally collate all these different files into a single file. This process is very similar to what happens in Bigtable.

A typical read operation will first query the in-memory structure before looking into the files on disk. If a disk hit is needed, the files are looked at in order of newest to oldest. For some reads, a disk lookup could occur which looks up a key in multiple files on disk. In order to prevent looking into files that do not contain the key, a bloom filter which summarizes the keys in the file is also stored in each data file and as well as kept in memory. This bloom filter is first consulted to check if the key being looked up does indeed exist in a given file.

A key in a column family could have many columns. In order to prevent scanning of every column on disk, we maintain column indexes which allow us to jump to the right chunk on disk for column retrieval. This is done by generating indeces at every 256K chunk boundary as the columns for a given key are being serialized and written out to disk. This boundary is configurable, but facebook has found that 256K works well in their production workloads.


Implementation Details
^^^^^^^^^^^^^^^^^^^^^^
Cassandra is mainly made up of three abstractions: the partitioning module, cluster membership & failure detection module, and the storage engine module. Each of these modules follow something along the lines of *staged event-driven architecture (SEDA)*, which decomposes a complex, event driven application into a set of stages connected by queues. Message processing pipeline and task pipeline are used to refer to the queues and inter-module data flow in this system.

The cluster membership & failure detection module is built on top of a network layer which uses non-blocking I/O. The system control messages rely on UDP, while the application related messages for replication and request routing rely on TCP.

The request routing modules (ie: the other two?) are implemented using a certain state machine. When a read/write request arrives at any node in the cluster, the state machine morphs through the following states (excluding failure scenarios for now):

1) identify the node(s) that own the data for the key
2) route the requests to the nodes and wait ont he responses to arrive
3) if the replies do not arrive within a configured timeout value, fail the request and return to the client
4) figure out the latest response based on timestamp
5) schedule a repair of the data at any replica if they do not have the latest piece of data.

The system can be configured to perform either synchronous or asynchronous writes. While asynchronous writes allow a very high write throughput, synchronous writes require a quorum of responses before a response is passed back to the client.

As for the commit log, it is rolled over to a new file every 128MB. The write operation into the commit log can either be in normal mode or in fast sync mode. In the fast sync mode, the writes to the commit log are buffered and we also dump the in-memory data structure to disk in a buffered fashion. As such, this mode has the potential for data loss upon a machine crash.

Cassandra morphs all writes to disk into a sequential format, and the files written to disk are never mutated. This means no locks need to be taken when reading the files. TODO: how is old data removed? during compaction process?

The Cassandra system indexes all data based on primary key. The data file on disk is broken down into a sequence of blocks. Each block contains at most 128 keys and is demarcated by a block index. The block index captures the relative offset of a key within the block and the size of its data. When an in-memery data structure is dumped to disk, a block index is generated and their offsets written out to disk as indices. This index is also maintained in memory for fast access.

As stated prior, the number of data files on disk will increase over time. The compaction process, very much like the Bigtable system, will merge multiple files into one; essentially merge sort on a bunch of sorted data files. The system will always compact files that are close to each other with respect to their sizes (ie: a 100GB file will never be compacted together with a sub-50GB files). Periodically a major compaction process is run to compact all related data files into one big file. This compaction process is disk I/O intensive and can be optimized so as not to affect incoming read requests.


Practical Noteable
------------------
* Setting a value of PHI to 5 on a 100 node cluster resulted in an average node failure detection time of 15 seconds
* Cassandra is well integrated with Ganglia
* Facebook's inbox was holding around 50+TB on a 150 node east/west cost cluster in 2009
