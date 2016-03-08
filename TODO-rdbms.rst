Relational Databases
====================
.. _rdbms:

# TODO: In addition to the ACID section below, review BASE(basically available, soft state, eventually consistent). BASE is typically used where ACID does not scale

Indexes
-------

Clustered Index
^^^^^^^^^^^^^^^
- This is a sorted index. An example would be a phone book. A clustered index is an index which *physically* orders the data (the actual bits on disk) in a certain way, and when new data arrives it is saved in the same order.
- A caveat with clustered indexes is that *only one can be created on a given database table*. This is because clustered indexes enforce data order - you can't enforce data order on two rows of the same table as the orders of each row would inevitably conflict.
- Additionally, clustered indexes increase write time because when new data arrives, all of the data has to be rearranged. On the bright side though, they can greatly increase the read performance from the table.

Non-Clustered Index
^^^^^^^^^^^^^^^^^^^
- These are the type that we use the most. These indexes *keep a separate ordered list* that has *pointers to the physical rows*.
- Unlike the clustered index, a table can have many non-clustered indexes. But the caveat with these indexes is that each new index will increase the time it takes to write new records.
- To summarize, non-clustered indexes *do not order* the data physically, they just keep a list of the data order.






~~Database Shit~~
-Research shows that the four common sources of overhead in database management systems are: logging (19%), latching (19%), locking (17%), B-tree and buffer management operations (35%)
((Locks protect data during transactions. Another process, latching, controls access to physical pages. Latches are very lightweight, short-term synchronization objects protecting actions that do not need to be locked for the life of a transaction.))


::ACID::
ACID (Atomicity, Consistency, Isolation, Durability) is a set of properties that guarantee that database transactions are processed reliably. 
-Atomicity requires that each transaction is "all or nothing": if one part of the transaction fails, the entire transaction fails, and the database state is left unchanged
-The consistency property ensures that any transaction will bring the database from one valid state to another.
-The isolation property ensures that the concurrent execution of transactions results in a system state that would be obtained if transactions were executed serially, i.e. one after the other. Providing isolation is the main goal of concurrency control. Depending on concurrency control method, the effects of an incomplete transaction might not even be visible to another transaction
-Durability means that once a transaction has been committed, it will remain so, even in the event of power loss, crashes, or errors. Transactions/other shit are usually kept in some sort of non volatile memory (eg: mysql-log on disk)


::MapReduce::
So, MapReduce does what it says in its name. First, it Maps data. What this means is that the master node takes input, divides it into smaller sub problems, and then distributes them to worker nodes. The node may reduce the information in those files to key/value pairs, or just into common queues (such as sorting students by first name into queues, one queue for each name) (filtering and sorting). It may also remove duplicates or only keep the highest value for keys that are the same, or divide the problem into smaller sub problems, or whatever else. Many Map jobs are run at the same time on different files. After the Map jobs are done, the results are all passed to a Reduce job. This reduce job combines all the results together and performs some sort of user-inputted operation/summary on the information (such as counting the number of students in each queue, yielding name frequencies, or combining all unique keys and displaying the highest value)

This is faster than just having a single task go through all the data serially, and also requires a ton less memory and compute resources assigned to just a single process. In essence, it is a method to allow huge data sets to be processed in a distributed fashion.

::NoSQL::

-Good for people who require a distributed system that can span datacenters while handling failure scenarios, who are not worried about the extreme consistency rules a relational DB may implement. NoSQL systems, because they have focussed on scale, tend to exploit partitions, tend not use heavy strict consistency protocols, and so are well positioned to operate in distributed scenarios.

-Write performance :: At 80 MB/s it takes a day to store 7TB so writes need to be distributed over a cluster, which implies key-value access, MapReduce, replication, fault tolerance, consistency issues, and all the rest. For faster writes in-memory systems can be used

-Fast key/value store access :: Why is key/value store fast? Pass a key to a hashing algorithm, and you get the same "location" output every time of where the value is stored. You end up not having to search for the value. Basically an index per data item, rather than choosing an index per column as you would in an RDBMS

-flexible schema/datatypes(eg: JSON), no SPOF

-Programmer ease of use :: Programmers want to work with keys, values, JSON, Javascript stored procedures, HTTP, and so on. End users typically want to work on data using SQL, but this preference should not permeate throughout all datastore decisions.

-Availability vs Consistency vs Failure Handling :: Relational databases pick strong consistency which means they can't tolerate a partition failure. In the end this is a business decision and should be decided on a case by case basis. Does your app even care about consistency? Are a few drops OK? Does your app need strong or weak consistency? Is availability more important or is consistency? Will being down be more costly than being wrong?


