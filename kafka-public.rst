.. _kafka:

Kafka
=====

http://kafka.apache.org/documentation.html

If you're new to kafka, skip to :ref:`kafka-general`. If you just want to see a quick list of reference commands with regards to topic modification, performance testing, mirrormaker, monitoring setup, and maintenance, skip to :ref:`kafka-quicknotes`.

.. _kafka-design:

DESIGN NOTES
------------

OVERVIEW
^^^^^^^^
- Do edge processing. Cut down on inter-DC traffic
- Increase resiliency of data transport layer
- 150TB/day minimum
- Aiming for repl factor 2 with 24hrs retention


PARTITIONING
^^^^^^^^^^^^
- 3 node cluster on 1gig uplinks, no expansion expected, 6 partitions and repl factor 2 is a good default. Double or triple if your consumers are slow.
- 3 node cluster on 10gig uplinks, no expansion expected, 30 partitions and repl factor 2 is a good default. Double or triple if your consumers are slow or you have more consumers per group than num of partitions. 60+ partitions is better for (redacted) topics as they have a high rate of data.
- Linkedin:
  - Makes sure each individual partition is under 50GB over a 4 day retention period as they see spikey lag problems in mirrormaker when exceeding this limit. They sometimes see this problem even with 30GB partition sizes. We push more data than this (though probably less msgs/sec), and might have to consider using more than 60 partitions per BE topic.

  "As a note, we have up to 5000 partitions per broker right now on current
  hardware, and we're moving to new hardware (more disk, 256 GB of memory,
  10gig interfaces) where we're going to have up to 12,000. Our default
  partition count for most clusters is 8, and we've got topics up to 512
  partitions in some places just taking into account the produce rate alone
  (not counting those 720-partition topics that aren't that busy). Many of
  our brokers run with over 10k open file handles for regular files alone,
  and over 50k open when you include network."

- When choosing number of partitions, producer and consumer count and individual consumer bandwidth are of note. A minimum of ten 1gig consumers are needed to saturate a single topic from a single 10gig broker, therefore at least 10 partitions per broker would be needed in this scenario. This assumes your consumers can process at gigabit speeds!
- Upon broker failure / unclean shutdown, partition leader election takes around 5ms per partition. Multiply this by 1000 partitions and you've got 5 seconds of downtime + however much time the broker failure took to detect
  - Suppose also that the controller broker fails. A new broker needs to be elected, which will then look in zookeeper to read the metadata of every partition. This may take around 2ms per partition, so with 1000 partitions factor in another 2 seconds downtime + broker controller election
- Replicating 1000 partitions from one broker to another adds about 20ms of latency. If this is too much for your real-time application, use less partitions or share topic between a larger number of brokers
- Giant partitions are not really wanted as they take longer to migrate and work with administratively. If a topic is expected to grow to a very large size, increase partition count a bit (with respect to num of brokers)
- It's a good idea to keep partitions per broker below 4000. In general, the less partitions the better so long as you can keep your performance and per-partition size goals
- LinkedIn runs 31k+ topics with 350k+ partitions on 1100+ brokers (http://events.linuxfoundation.org/sites/events/files/slides/Kafka%20At%20Scale.pdf). This averages ~11 partitions per topic (!!unknown average cluster size!!)
- Ideally, in our publisher we want to use a partition key such that we can get common data onto the same partition. What can we key off of? This choice is determined by how we want to process the data on the other side. For example, if we partition by DSP and we have a samza/other job that wants to grab and calculate all metrics from a specific DSP, having that DSP exist on a single partition allows us to avoid a more costly multi-partition-consume operation.
  - It is possible to calculate partition key several times. ie: hash once for userID, hash a second time for adID, use result to choose partition
  - Key/hash is going to change if partition count for a topic changes. Keep this in mind when initially creating a topic, such that you don't have to increase partition count whenever you expand your broker count


TOPIC NAMING
^^^^^^^^^^^^
Ultimately, our topic naming should be something that our devs across teams can expect and understand, and something that makes sense when considering an aggregation of topics being sent from multiple sites down to a larger data processing site.

(redacted)

DELINEATING MESSAGES BY TIME
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(redacted)

3)
- Don't put time logic into kafka. Instead, Use 'timestamp' field in (redacted) message:
  - This makes it the consumers / data processing application's responsibility to deserialize and parse the protobuf message in order to see which day the data is part of
  - This is the most accurate timestamp because it is generated by the AE/BE/Other
  - This keeps our messages clean and consistent per topic. Beneficial for simpler monitoring and malformed message / message structure exceptions
  - Disadvantage is that you have to deserialize the message in order to know whether you would like to continue processing further messages

Option 3 suits Kafka's design philosophy.


COMPRESSION
^^^^^^^^^^^
- The java producer has a built in compression feature, and the java consumer has a complimentary built in decompression feature.
  - Compression is performed by the producer, who takes a handful of messages, compresses them, wraps them in a "compressed message set" and then publishes that message set as a single message to kafka. This message is differentiated by a magic byte set in its header, letting downstream consumers know that it is a compressed set
  - When the provided java consumer sees this magic byte as it's consuming, it will grab the message and transparently unpack it, and then output one message at a time from that message set
  - The compressed message set is its own message, it has one offset. Therefore, when the consumer consumes the message set, it will only advance its consumer offset position by one, even though the message set has several messages in it. This is expected; however, in the event of consumer failure and message set re-transmission, you may end up with more duplicate messages than you may expect.
- Most alternate clients i've seen (eg: kafkacat) offer compression/decompression per spec as well
- Java snappy has been extremely unstable in our usage. lz4 is faster and much more stable, but is currently unsupported by librdkafka (C) clients.


PRODUCING
^^^^^^^^^
0.8.2 Java producer (old)

- Publish new messages to a specific topic *and an optional partition* (use partitioner.class to define part. scheme)
- Threadsafe. You may share the same producer among your threads.
- The producer manages a single background thread that does I/O, as well as a TCP connection to each broker it needs to communicate with.
- Failure to close the producer after use will leak I/O resources
- When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0,1 or all (-1) replicas.
  - Note that -1 means all current in-sync replicas...if an ISR is currently out of sync, publishes with acks=-1 will still succeed. If this is not wanted, you may specify the number of ISR's you'd like a response from (eg:acks=2) before the write is successful. Keep in mind that this will halt all writes if your acks number is higher than the available brokers.


CONSUMING
^^^^^^^^^
Deprecated section. 0.9 consumer has no separation of consumer. This section needs updating.

- SimpleConsumer: Allows you to read a message multiple times
- SimpleConsumer: Allows you to consume only a subset of partitions in a topic in a process
- SimpleConsumer: Allows you fine grained transaction control, allows making sure a message is processed 'just once'
- SimpleConsumer: You must keep track of your own offset to know where you left off consuming
- SimpleConsumer: You must figure out which broker is lead broker for a topic and partition
- SimpleConsumer: You must handle broker leader changes
- HighLevelConsumer: Don't care about handling message offsets. Stores last offset read from a specific partition in Zookeeper, stored under a Consumer Group name
- HighLevelConsumer: Kafka doles out partition assignments per thread connected to it under a certain consumer group. Your High Level Consumer should ideally have as many threads as there are partitions+replications
- HighLevelConsumer: If you have less threads than there are partitions, there will be no guarantee of ordering aside from sequential offset number


MIRRORMAKER
^^^^^^^^^^^
- Best practice is to keep mirrormaker local to the target cluster. This makes sense as consuming can be controlled by offsets, so upon network interruption it's not a big deal. Network interruption when trying to produce, however, results in message timeouts and loss.
- Target kafka clusters are termed "aggregate clusters". These clusters host an aggregate of topics from multiple other clusters in various DC's
- LinkedIn triple bolds and shouts that you should never ever ever produce to an aggregate cluster. This means that your mirrormaker processes should be the only ones ever producing to your aggregate cluster.
  - This means if your aggregation/main datacenter also provides the same services as your edge cluster (which all mirrormaker data back to your main DC for aggregation), you should also set up a separate "edge" cluster at your main datacenter and then mirrormaker that to your "aggregated results" kafka cluster even though it's local (ie: don't produce to your aggregate cluster)
  - This makes sense from an ETL perspective and just as an orderly segregation of services perspective. Not really a super show stopper but would be best practice.
- Mirrormaker usually needs to be more resilient than normal...might be able to afford smaller batches and acks=-1
- Messages are always going to be decompressed by mirrormaker and then recompressed upon publishing to the destination cluster. This is necessary for KeyedMessage and many other publishing features to work. There is ongoing work to perhaps provide the option to simply publish the compressed MessageSet onwards to the destination DC without decompressing.
- Partitions are not preserved! screws up your key based partitioning. You must use the same partitioner class at the mirrormaker publisher end to get accurate message placement
- If your aggregate clusters are where you really need the data, then your retention period on your remote clusters should only be long enough to cover mirrormaker (read: network) problems
- ***!!!Run a separate mirrormaker process for important topics!!!** If your main process fucks up, you don't want it affecting the high priority topics (ie: topics that are used for hourly reporting, or topics that change "live" search results etc)
  - You may also consider running a separate mirrormaker process for bloated topics, such that they won't affect the others
  - Less time to catch up if you fall behind


MONITORING
^^^^^^^^^^
- Ensure JMX options are set in kafka-run-class.sh included with package, or call those out in puppet. This is the line you need:
  bin/kafka-run-class.sh:  KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.port=9999 "

- In addition to your standard process, disk, other server monitoring, you should be watching at a bare minimum your consumer offset lag time, as well as your broker cluster health (number of in-sync-replicas, replica lag time). It's preferrable to use a tool like Burrow in order to monitor your consumer lag, but you can also do it from included scripts.
  LAG=$(/opt/kafka/kafka_install/bin/kafka-run-class.sh kafka.tools.ConsumerOffsetChecker --group "${GROUP}" --zkconnect "${ZK}" --topic "${TOPIC}" | grep $TOPIC | awk -F' ' '{ SUM += $6 } END { printf "%d", SUM/1024/1024 }')

- [Running Kafka at Scale - Linkedin](https://engineering.linkedin.com/kafka/running-kafka-scale)
- Linkedin uses an internal "Kafka Audit" tool to ensure a message got from point A to point Z. So, every producer keeps track of how many messages it has produced over a certain time period. It then periodically send this count to an auditing topic. Additionally, each consumer they use also has a counter for how many messages it has consumed over a certain time period. It also periodically sends this count to an auditing topic. A separate consumer then consumes this audit topic, pushes the numbers to a DB, and there is a UI in front of the DB. They then can compare the #produced and #consumed messages, spitting an alert if there's a mismatch (duplicates, missing, etc).
  - Audit message content includes a timestamp and service+hostname header, start and end timestamp (for the produced messages it counted), topic name, tier (tier is on what tier the audit message was generated, eg: 0=remote_source_application, 3=mirrormaker_aggregate), and message count itself.
  - Concerns here are that since we're only counting messages, duplicate messages can cover message loss. It's also difficult to keep track of complex message flows


OPEN QUESTIONS
^^^^^^^^^^^^^^
- How much do we care about ordering?
- What is going to be pulling data from kafka? 
  - (edge processing, send aggregate results to LAS? What do we want to process at the edge?)
- Is all of our processing done in 24hr chunks?


BUGS & GOTCHAS
^^^^^^^^^^^^^^
- This one can sometimes happen if your consumer breaks from zookeeper at the right time. To fix it, reset the offset for your consumer group in zookeeper and delete anything spurious/temporary. Alternately, restart your consumers with a different consumer group ID.
  [2015-11-13 11:36:40,299] FATAL [mirrormaker-thread-1] Mirror maker thread failure due to  (kafka.tools.MirrorMaker$MirrorMakerThread)
  kafka.common.ConsumerRebalanceFailedException:
- You should avoid using zookeeper for your offset commits. Use 0.8.3 or newer and commit them to kafka instead.
- Snappy java sucks. If you're getting corruption errors or any type of failed produce errors, especially when restarting a broker, try using lz4 or no compression instead. Keep in mind librdkafka (ie: C-based) clients don't currently support lz4


NOTABLES
^^^^^^^^
- Kafka encourages large topics rather than many small topics
- A producer can choose a random partition to write to, but in a production system, you probably want to choose which partition to write to.
- Each partition must fit on one machine. Each partition is ordered. Each partition is made up of several log files..
- Each partition is consumed by only one consumer in a consumer group. Many partitions can be consumed by a single process though. You could have 1000 partitions consumed by a single process
- So, the partition count is a bound on the maximum consumer parallelism. More partitions means you can have more consumers, which means potentially faster consuming.
- Taken to an extreme, too many partitions means many files. This can lead to smaller writes if you don't have enough memory to properly buffer a batch of writes. If you have enough brokers, this shouldn't be a problem.
- Each partition corresponds to several znodes in zookeeper. Zookeeper keeps everything in memory, so beware
- More partitions means longer leader failover time. Each partition can be handled in milliseconds, but with thousands of partitions, this can add up
- The broker checkpoints the consumer position (as of 0.8.2) via an API call. It's stored at one offset per partition, so the more partitions, the more expensive the position checkpoint is
- It is possible to later expand the number of partitions; however, the broker will not attempt to reorganize data in the topic. If you are depending on this key-based semantic and numpartitions/numkeys changes and your data isn't in the expected place, you have to manually copy messages over to where you expect them to be
- Use a separate consumer connector per topic if feasible (https://cwiki.apache.org/confluence/display/KAFKA/FAQ#FAQ-Myconsumerseemstohavestopped,why?)

- TIME: Kafka allows getting the latest or earliest message offset by unix timestamp, but it does so at log segment granularity. So to get more accurate results you should use log.roll.ms rather than log.segment.bytes to roll your log segments. Be careful of how many files you create here.


FROM THE INTERNETS
^^^^^^^^^^^^^^^^^^
  ~~
  A few things I've learned:
  
  -Don't break things up into separate topics unless the data in them is truly independent.
  -Consumer behavior can be extremely variable, don't assume you will always be consuming as fast as you are producing. Don't assume the lag on all your partitions will be similar.
  -Keep time related messages in the same partition.
  -Design a partitioning scheme, so that the owner of one partition can stop consuming for a long period of time and your application will be minimally impacted. (for example, partitioning by transaction id). Knowing what data will end up on what partitions will allow you to differentiate between data you have and data you don't.
  ~~  

  ~~
  When the partitioning key is not specified or null, a producer will pick a random partition and stick to it for some time (default is 10 mins) before switching to another one. So, if there are fewer producers than partitions, at a given point of time, some partitions may not receive any data. Topic partition sizes may be lopsided for a time due to this as well.
  ~~


.. _kafka-general:

GENERAL
-------
- Kafka maintains feeds of messages in categories called Topics
- Processes that publish messages to a kafka topic are called Producers
- Processes that subscribe to topics are called Consumers

So,

  Producer ---> [kafka cluster(topic)] ---> Consumer

A "client" refers to either a producer or a consumer. There's lots of
clients out there, using various languages https://cwiki.apache.org/confluence/display/KAFKA/Clients

BROKERS
^^^^^^^
- A broker is an instance of kafka. It uses zookeeper to know about other brokers in its cluster.
- Each broker can be queried to find out information about the cluster, such as describing a topic, finding out your replication factor, which nodes are leaders for which partitions, etc.
- There is a "Controller" broker in each cluster which handles partition leader elections, updating zookeeper, etc
- Read more in the "CLUSTERING" section

TOPICS
^^^^^^
- A topic contains one or more partitions. Partitioning data allows for dataset sizes larger than a single server.
- Ordering guarantees are provided on a per-partition basis. When a topic is split into partitions, the only guarantee on ordering is within the partitions themselves.
- Total ordering guarantees (within kafka, without requiring external client logic) can only be accomplished by using topics with a single partition, and a transactional publishing model
- You can either create a topic (and define the number of partitions you want) with kafka-topics.sh
or some other script, or alternatively you can configure your brokers to auto-create topics when a non-existent topic is published to
- Each published message is added to the end of a partition and assigned a sequential id called the offset (unique)
- The kafka cluster retains all published messages for a configurable period of time (or size limit). Consuming a message does not remove it
- A Consumer can consume any (offset)message it likes, in any order

Topic Creation Example: 

  bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 2 --partitions 1 --topic test
  bin/kafka-topics.sh --list --zookeeper localhost:2181

PARTITIONS
^^^^^^^^^^
- Number of partitions is defined upon topic creation, as is number of replicas
- partitions are distributed across servers in a kafka cluster. Kafka does this itself upon topic creation
- You can run bin/kafka-create-topic.sh on one of your brokers, specifying number of replicas and number of partitions. Alternatively, kafka can auto-create topics when a non-existant topic is published to. In this case, it uses defaults for numreplicas and numpartitions.
- Partitions are represented as a set of log files on disk. You can configure how big you want your log files to be before new writes go to a new log.
- When you define a maximum topic size or maximum age, these values apply to your partitions, not the topic as a whole. Once a partition log file hits a certain age, or the maximum partition size is reached (size of all log files added together), the oldest log is deleted from disk.
- Each partition can be replicated across a configurable number of servers. You end up with one "leader" for that partition, and zero or more "followers." If a leader dies, a follower picks up.
- Each server acts as a leader for some of its partitions and a follower for others
- The controller detects broker failures and elects a new leader for each affected partition. The detection is done via an internal broker RPC, not via zookeeper. The controller will however update zookeeper after it has chosen a new leader for an affected partition.
- Read rollout-notes for an idea of how many partitions you should choose for your topics

PRODUCERS
^^^^^^^^^^
- Producers publish data to the topics of their choice. They query kafka brokers to get metadata about what topics, partitions, and replicas are available. (future producers: just point them at two or three kafka's to grab initial bootstrap data, they'll use that data to get the rest of the brokers in a cluster)
- Kafka comes with an example producer, kafka-console-producer.sh, which accepts stdin(per-line), or raw input (run it, then type stuff in)
- The producer is responsible for choosing which message to assign to which partition within the topic. This can be done round robin, or according to some function (like a hash on a key in the msg)
- The producer can query kafka to see if it has an existing topic, or it can choose to create its own topic. It can pass how many partitions, replicas etc it wants for this new topic, or let kafka use its defaults.
- When writing to Kafka, producers can choose whether they wait for the message to be acknowledged by 0,1 “all” (-1) *in-sync* replicas, or x number of replicas. Note that -1 means all *current in-sync replicas*...if a replica is currently out of sync, publishes with acks=-1 will still succeed. If this is not wanted, you may specify the minimum number of ISR's you'd like a response from (eg:acks=2) before the write is successful. Keep in mind that this will halt all writes if your acks number is higher than the available brokers.

CONSUMERS
^^^^^^^^^^
- kafka-console-consumer.sh comes with kafka. It'll dump messages to stdout
  bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic test --from-beginning
- Consumers label themselves with a consumer group name
- Consumers read data from topics. Kafka maintains a consumer group list, and assigns a partition in a topic per consumer in a consumer group.
- Each partition in a topic is delivered to *one* consumer instance (thread) within each subscribing consumer group. 
  - This allows for multiple consumers in a consumer group to process a topic in parallel, because only one of them is consuming each partition.
  -This means there should not be more consumer instances (in the same consumer group) than there are partitions, extras are left idle
  - Multiple consumer groups can subscribe to the same topic. You can put every consumer into its own consumer group if you want.
- One consumer per partition model allows kafka to ensure the ordered delivery of a partition.
  - If you need total ordering guarantees (ie: the entire topic, not just a partition in the topic), you have to make a topic with a single partition (and thereby a single consumer)...OR some sort of ordering inside your data itself, which something can re-order once all the consumers pull it together.
- As of 0.8.2, kafka provides an API call that allows consumers to publish their checkpoint offset. 
  - Internally, the implementation of offset storage is just a compacted kafka topic (__consumer_offsets) keyed on the consumer's group, topic, and partition
  - The offset commit provides acks=-1 durability
  - Kafka maintains an in-mem view of this tuple: <consumer group, topic, partition>, so offset fetch reqs can happen very quickly without the need for scanning the compacted __consumer_offsets topic
  - Previously, it was the consumers responsibility to push its current offset location to zookeeper

GUARANTEES
^^^^^^^^^^
- Messages sent to kafka by one producer to a particular topic partition will be appended in the order they are sent, ie: the first sent message will have a lower offset in the log than the second sent message. This is a guarantee built into your producer.
- A consumer sees messages in the order they are stored in the log
- For a topic set to replication factor N, we will tolerate up to N-1 server failures without losing any messages committed to the log. Eg: replication factor 3 can withstand 2 server failures.

CLUSTERING
^^^^^^^^^^
- kafka nodes find out about each other via zookeeper (zookeeper.connect= in your server.properties). By default, all kafka nodes who are connected to the same zookeeper cluster will be part of the same cluster.
  - To set up multiple kafka clusters connecting to the same zookeeper cluster, you must define a 'chroot' address on your zookeeper.connect line. eg:
zookeeper.connect=hostname1:port1,hostname2:port2,hostname3:port3/chroot/path
  - Note that you must create this chroot path yourself prior to starting up your kafka cluster
  - this will put that kafka's nodes/leaves under its own path, thereby separating your cluster out from the main path.
  - If you are running chroots as above (*and a kafka version less than 0.8.2*), you also have to configure your consumers to use the appropriate chroot path. In consumer.properties it's the same zookeeper.connect line.
- After zookeeper discovery, each kafka cluster designates a "controller". It will be responsible for:
  - Leadership change of a partition (though each leader can still independently update the ISR list)
  - New topics; deleted topics
  - Replica re-assignment
  - https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Controller+Internals
- Broker failure detection is done via direct RPC, internal kafka functions - not zookeeper
- Controller death could be detected by controller.socket.timeout.ms configured on each broker
- Communication between the controller and the rest of the brokers is done through RPC
- The controller is the one that commits changes (new topics, leadership changes etc.) to zookeeper

COMPACTION
^^^^^^^^^^
http://kafka.apache.org/documentation.html#compaction
- You have the option to either compact or delete log segments once you hit either a certain time limit, or size limit. The idea is to selectively remove records where we have a more recent update with the same primary key.
- can be set per topic at creation, or using alter topic. Default log.cleanup.policy is delete.
- Let's say you're pushing messages to kafka that look like this "uid123 herp=derp", "uid123 herp=lerp", "uid123..." etc etc. You're updating "the same value" over time, perhaps it's a user updating his/her new email address or info. Log compaction will look at a unique key in your logs(messages) and then remove all but the latest update related to that key.
- Compaction allows consumers who are unable to keep up with the log (or crashed) to see the last value a key was set to
- You can set your key's value to 0 to mark that key for deletion (happens 24hrs later by default)
- compaction is not compatable with compressed topics
- your message offset never changes. Some get deleted, the newest stays, and the offset stays the same
- Take note of log.cleaner. options such that performance is not an issue
- Be aware that your topic is going to continue growing until you intervene, so be aware of how many primary keys you have and your primary key growth

API DEETS
^^^^^^^^^
**DEPRECATED NOTES AS OF 0.9**. The following info is mostly deprecated as of 0.8.3 (0.9), but still gives an idea of how things work.

**Producer-API**

The Producer API wraps two low level producers. These are kafka.producer.SyncProducer and kafka.producer.async.AsyncProducer. The goal is to expose all the producer functionality through a single API to the client.
The API provides the ability to batch multiple produce requests (when procer.type=async). As events enter a queue, they are buffered until queue.time or batch.size is reached. Then a background thread kafka.producer.async.ProducerSendThread dequeues the batch of data and lets kafka.producer.EventHandler serialize and send the data to the appropriate broker partition. Monitoring/stats can be done by implementing kafka.producer.async.CallbackHandler to inject callbacks at various stages.
The API also provides software load-balancing between partitions via an optionally user-specified kafka.producer.Partitioner. Otherwise, you can provide a key. If you do not include a key, kafka will assign the message to a random partition. You may also define your own partition.scheme to key off and direct certain data to certain partitions.

**Consumer-API**


There's two levels. The "simple" API maintains a connection to a single broker and has a close correspondance with the network requests sent to the server. It's stateless and has the offset passed in every request, which allows the user to maintain metadata however they choose.
The "high-level" API hides the details of brokers from the consumer. It allows a consumer to consume off a cluster of machines without concern of the underlying topology. It also maintains state of what has been consumed. It also allows you to subscribe to (or ignore) topics based on a regex.
- SimpleConsumer: Allows you to read a message multiple times
- SimpleConsumer: Allows you to consume only a subset of partitions in a topic in a process
- SimpleConsumer: Allows you fine grained transaction control, allows making sure a message is processed 'just once'
- SimpleConsumer: You must keep track of your own offset to know where you left off consuming
- SimpleConsumer: You must figure out which broker is lead broker for a topic and partition
- SimpleConsumer: You must handle broker leader changes
- HighLevelConsumer: Don't care about handling message offsets. Stores last offset read from a specific partition in Zookeeper, stored under a Consumer Group name
- HighLevelConsumer: Kafka doles out partition assignments per thread connected to it under a certain consumer group. Your High Level Consumer should ideally have as many threads as there are partitions+replications
- HighLevelConsumer: If you have less threads than there are partitions, there will be no guarantee of ordering aside from sequential offset number

CONSUMER OFFSETS
^^^^^^^^^^^^^^^^
- With 0.8.2 (0.8.3 really) comes the ability to do broker-committed offsets. This means that the consumer api has the option to commit your offsets to a topic called __consumer_offsets on your brokers, rather than having to use zookeeper. There's a bunch of new config options for this - check the docs for offsets.*
- The topic is created as soon as the first consumer using the new API commits an offset to kafka. This topic is created with 50 partitions, repl factor 3, and log compaction on by default
- Commits to __consumer_offsets by the consumer API use groupID, Topic, and PartitionID to key off of in order to determine which partition of __consumer_offsets to save the commit message to.
- The default offsets.topic.num.partitions=50 seems quite high, and 100-200 partitions are "recommended" for production. 
  - Keying offset commits across many partitions may mildly improve performance of consumers looking up offset values due to smaller partition sizes, but I'm not sure this justifies the extra 5ms-per-partition, 2ms-per-partition leader initialization time, and replica thread / other used resources. 
- This feature may be buggy. We're currently seeing a random, some brokers but not others, 3300% idle increase in CPU utilization with __consumer_offsets @ 50 partitions and repl 3 on a 3 node cluster. Not sure yet how it's related

MESSAGES
^^^^^^^^
- Messages consist of a fixed-size header and a variable-length opaque byte array payload. The header contains a format version, and a CRC32 checksum to detect corruption or truncation. Put whatever you want in the payload, kafka doesn't care.
- Header has:
  1 byte magic identifier to allow format changes
  {{ONLY if magic byte set}} 1 byte "attributes" identifier (eg: compression enabled, type of codec used)
  4 byte CRC32
  N byte payload

LOG
^^^
- A topic like 3p2r (3 partitions, repl factor 2) is going to have three directories on disk - 3p2r_0 3p2r_1 3p2r_2. If you've got three brokers, one partition leader may have 3p2r_0 while another will have _1. A replication partner may also have a 3p2r_0 directory even though it's not the leader for it, because it's a replication partner.
- Two files are saved. An .index file, and a .log file. The .index file contains 64-bit integer offsets giving the byte position of the start of each message in a .log file. It's a mapping of offset to physical location. The .log file holds the actual data.
- The format of the log files saved to disk is a sequence of log entries. The format for a log entry is the same as above, but has a message length integer:
  4 byte message length integer (1+4+n)
  1 byte "magic" value
  4 byte crc
  n byte payload
**::Writes**
- A log file will grow to a certain size (default 1GB), and then begin writing to separate .index/.log files. Each log file is named with the offset counter of the first message it contains. So, if you're saving 64KB messages and rotating at 1GB, that's around 15625 messages per. It takes a bit for kafka to notice and rotate, so typically you're going to have log files a bit larger than 1GB and having more than your expected # of messages per log file. You may end up with 00000000000000000000.index and then 00000000000000016767.index with 64KB files @ 1GB rotation. So, your first .log file has 16766 messages in it.
**::Reads**
- Give the offset (ie:counter) and the max chunk size (intended to be larger than any single message could be, but in the event of an abnormally large message, retry the read doubling the buffer size each try until the message is read successfully).

BIG SLOW DISK IS GOOD
^^^^^^^^^^^^^^^^^^^^^
http://kafka.apache.org/documentation.html#persistence
- It's common perception that disks are slow and should be avoided. However, because of kafka's sequential nature, it can take great advantage of the operating systems disk read-ahead and write-behind techniques that prefetch data in large block multiples and group smaller logical writes into large physical writes.
- Additionally, building on top of JVM means having to use java's ... memory management. The memory overhead of objects is very high, often doubling the size of the data stored (or worse). Additionally, Java garbage collection becomes increasingly fiddly and slow as the in-heap data increases.
- So what to do? Write the stuff out to a file on disk immediately. It just gets written to your pagecache, which is going to take up way less space than in mem java. Data is also stored as a compact bytes structure rather than individual objects. Also, the cache stays warm across process reboots rather than being cleared. And when data needs to be retrieved, you get a direct pointer to the data in memory. You also end up not having to worry about "in memory" vs "on-disk" information, now it's the OS's job.

NOTEABLE CONFIGURATION NOTES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
http://kafka.apache.org/documentation.html#configuration
- message.max.bytes (1000000) : max size of a message the broker can receive from a producer. Synch this with the max fetch size your consumers use. You don't want messages too large for your consumers. Also keep in mind possible batched+compressed MessageSets, which may be many times the size of a single normal message!
- num.io.threads (8) : set this to as many threads as you have disks
- queued.max.requests (500) : number of requests that can pile up waiting for disk I/O before the network threads stop reading in new requests
- socket.send.buffer.bytes : socket.receive.buffer.byes (100*1024) : SO_SNDBUFF and SO_RCVBUFF respectively
- log.retention.{minutes,hours} (7d) : retention period. If both this and log.retention.bytes are set, it will do both. Whichever is hit first.
- log.retention.bytes (-1) : how big a single log (ie: partition) can grow before a log segment is deleted/compacted (topics are split into partitions (aka:logs), and logs are split into segments (default 1gig segments). Deletions happen to entire segments at once.
- log.flush.interval.messages (None) : sets your fsync time before messages in memory are sync'd to disk. It is strongly recommended to rely on replication rather than setting an fsync time, as this has a huge performance impact.
- default.replication.factor (1)
- replica.lag.time.max.ms (10000) : If a follower hasn't sent any fetch requests for this window of time, the leader will remove the follower from ISR (in-sync replicas) and treat it as dead.
- replica.lag.max.messages (4000) : If a replica falls more than this many messages behind the leader, the leader will remove the follower from ISR and treat it as dead.
replica.fetch.max.bytes (1024*1024) : how many bytes (per partition) to try to grab in one fetch to the leader
- num.replica.fetchers (1) : number of replication threads to the leader. Increasing this can increase the degree of I/O parallelism in the follower broker
- controlled.shutdown.enable (false) : This makes the broker attempt to transfer partition leadership to other brokers prior to shutting down. Speeds up unavailability window during shutdown. *WARN* Ensure your init script properly waits and terminates all child java processes prior to returning success, else restart will fail */WARN*
- auto.leader.rebalance.enable (true) : If this is enabled the controller will automatically try to balance leadership for partitions among the brokers by periodically returning leadership to the "preferred" replica for each partition if it is available.
  - leader.imbalance.per.broker.percentage (10) : The percentage of leader imbalance allowed per broker. The controller will rebalance leadership if this ratio goes above the configured value per broker.


DEPLOYMENT NOTES
^^^^^^^^^^^^^^^^
- Upon node failure, kafka doesn't know whether it'll be permanent or not. Maybe you want to replace it with a new broker, or make another existing broker part of the replication pool for that topic. The preferred method upon broker failure is to bring up a new broker (if it's a total replacement) with the same broker.id as your failed box. This way when you start it up it'll join, notice that it's way off, and start automatically replicating/recovering.
  - Other cluster resizing or rebalancing operations must be done manually, using bin/kafka-preferred-replica-election.sh or kafcat (not kafkacat, kafkat), or yahoo's kafka-manager
- kafka includes a bin/kafka-{producer,consumer}-perf-test.sh. This client utilizes batch processing, and can run multiple threads. It automatically counts for you, can push a specified # of messages, etc. Using this, we can easily max a gigabit link on each node of a 3-node kafka cluster using 64KB message sizes. We can also get around 1.2million 100byte publishes/sec out of this hardware from 3 2008 crappy blades.
- The java producer that comes with kafka has a compression.codec option. Enabling compression will cause the producer to buffer up a set of messages, wrap them in an eventMsg, compress that whole eventMsg, then send that message as a whole to your broker. This message's header will have its magic byte set along with a flag saying that this message is compressed. On the other side, the java kafka consumer has an iterator that can automatically detect these compressed eventMsgs, decompress the eventMsg, and then spit out each individual message.
- There's a nice little statically linked C client called kafkacat that is extremely useful for quick producing/consuming/troubleshooting. It accepts input from stdin if acting as a producer, or outputs to stdout if acting as a consumer. It also supports compression, and will automatically decompress MessageSets when consuming


STUFF TO WATCH
--------------
This section describes a list of kafka related tools and such to keep an eye on.


PRODUCERS/CONSUMERS
^^^^^^^^^^^^^^^^^^^
  [Kafkacat](https://github.com/edenhill/kafkacat) :: 'netcat' for kafka. Lightweight statically-linked producer/consumer client. Takes stdin and consumes to stdout. Extremely simple, versatile, I use it almost exclusively. librdkafka does not support lz4 at the moment.
  [Flasfka](https://github.com/travel-intelligence/flasfka) :: Expose kafka over python's simple web framework flask(http). Pretty neat-o. Limitations: utf-8 input only. Encode to base64 if you need to push arbitrary data to it. We use this for twittershitter
  [Bruce](https://github.com/tagged/bruce) :: C client that sits on a host and listens to a unix dgram socket. Your app then only has to send info in a simple binary format to a /dev/kafka_bruce. Saves devs from having to implement kafka API client code in their codebase.
  [Stealthly Syslog to Kafka](https://github.com/stealthly/go_kafka_client/tree/master/syslog) :: syslog->kafka producer, per SRD-29. Works fine
  [omkafka for rsyslog](http://www.rsyslog.com/doc/master/configuration/modules/omkafka.html) :: omkafka, builtin module for rsyslog to publish to kafka. Likely our best bet for syslog->kafka
  
  Choice of a client will ultimately be up to our devs:
  [Kafka Clients](https://cwiki.apache.org/confluence/display/KAFKA/Clients)


MONITORING RELATED
^^^^^^^^^^^^^^^^^^
  [Burrow](https://github.com/linkedin/Burrow) :: Consumer lag checker from linkedin. If you use nothing else, use this.
  [jmxtrans](https://github.com/jmxtrans/jmxtrans) :: Crappy but fast JMX monitoring tool, but has built in writer for openTSDB and many others. Will periodically poll for stats from mbeans exposed via JMX
  [collectd](https://collectd.org) :: Use collectd with jmxtrans or whatever else
  [tjconsole](https://github.com/m-szalik/tjconsole) :: Text jconsole! Discover what metrics are available to you over your JMX interface.
  [Dropwizard](https://github.com/dropwizard/metrics) :: The big main java metrics monitoring suite. Kafka uses this package to expose its stats
  [Logstash JMX Poller](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-jmx.html) :: Logstash has a jmx poller. This is much preferable to jmxtrans so long as it is able to scale
  [kafka-web-console](https://github.com/claudemamo/kafka-web-console) :: Web interface for monitoring kafka. Might be worth a look.
  [DCMonitor](https://github.com/shunfei/DCMonitor) :: Web interface for monitoring kafka. Might be worth a look.

ADMIN TOOLS
^^^^^^^^^^^
  [kafkat](https://github.com/airbnb/kafkat) :: Not to be confused with kafkacat. Simplified command line administration for kafka. Anything is better than those shit awful json-script-using kafka builtin tools...so check this out
  [kafka-manager](https://github.com/yahoo/kafka-manager) :: an admin tool from yahoo. Can handle partition migration and other stuff. Worth a look


.. _kafka-quicknotes:

QUICKNOTES
----------
These were written for kafka 0.8.2 and as such may not work with 0.9. Reference kafka documentation for updated versions of these commands if they do not work.

TOPIC CREATION, METADATA, TOPIC DELETION, ETC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Keep in mind all of these settings have defaults in server.properties. You only need to define these topic creation settings if you want to stray from the defaults.

  # Create some topics. 86400000s is 24hrs. USE THE .ms CONFIG OPTION!! .m and .h are always broken/breaking/not honoured (even in 0.9)
  ./kafka-topics.sh --zookeeper srv1003:2181 --create --topic 3p1r --partitions 3 --replication-factor 1
  ./kafka-topics.sh --zookeeper srv1003:2181 --create --topic 3p2r --partitions 3 --replication-factor 2 --config max.message.bytes=6553600 --config segment.bytes=8589934592 --config delete.retention.ms=86400000
  # Check for your newly created topics
  ./kafka-topics.sh --describe --zookeeper srv1002:2181
  # Alternately, you can use kafkacat 
  kafkacat -L -b srv1005
  
  # You need this enabled to delete topics. Enable it and restart all your brokers:
  #   server.properties:delete.topic.enable=true
  ./kafka-run-class.sh kafka.admin.TopicCommand --zookeeper 192.168.100.102:2181 --delete --topic 3p1r
  # Alter an existing topic.
  ./kafka-topics.sh --zookeeper localhost:2181 --alter --topic my-topic --config max.message.bytes=128000 --config retention.bytes=6000000000000
  ./kafka-topics.sh --zookeeper localhost:2181 --alter --topic my-topic --deleteConfig max.message.bytes

PRODUCER/CONSUMER RUNNING + PERFORMANCE TESTING
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  #Test multithreaded, 100byte msg default. Sync by default (acks=-1).
  ./kafka-producer-perf-test.sh --broker-list srv1005:9092,srv1007:9092,srv1008:9092 --messages 50000000 --topics 3p1r --threads 16
  #64KB message size
  #REQUIRES: Modify perf-test.sh KAFKA_HEAP_OPTS="-Xmx24576M" , or whatever you RAM situation permits
  ./kafka-producer-perf-test.sh --broker-list srv1005:9092,srv1007:9092,srv1008:9092 --messages 100000 --topics 3p1r --threads 16 --message-size 64000 --batch-size 50
  
  ./durr.sh | kafkacat -b srv1005 -t omgwtfbbq & CHILD_PID=$! ; sleep 5s ; kill -HUP $CHILD_PID
  cat 50mlinesofstuff | kafkacat -b srv1005,srv1007,srv1008 -t testymctesttopic
  #Can kick out ~184k msgs/sec single threaded, 100byte messages on crappy blade. Very fast single threaded performance, twice that of perf-test single threaded.

MIRRORMAKER
^^^^^^^^^^^
  # You don't need two consumer configs. Just shown here to show that a single mirrormaker process can read from multiple clusters
  bin/kafka-run-class.sh kafka.tools.MirrorMaker --consumer.config sourceCluster1Consumer.config --consumer.config sourceCluster2Consumer.config --num.streams 2 --producer.config targetClusterProducer.config --whitelist=".*"

  #Producer/Consumer config options are in documentation under Configuration. Here are some minimal examples:
  $ cat sourceCluster1Consumer.config
  group.id=mirrormaker.dc1
  zookeeper.connect=zoo0000:2181
  offsets.storage=kafka
  dual.commit.enabled=true
  
  #Note these are OLD producer config options. Use doc section "3.4 New Producer Configs" for 0.8.3+
  $ cat targetClusterProducer.config
  metadata.broker.list=kaf0000:9092
  #-1=wait for all ISRs. 0=dont wait. 1=wait for leader response
  request.required.acks=-1
  producer.type=sync
  serializer.class=kafka.serializer.DefaultEncoder
  compression.codec=snappy
  batch.num.messages=50

TEST IT
^^^^^^^
  bin/kafka-run-class.sh kafka.tools.ConsumerOffsetChecker --group mirrormaker.dc1 --zookeeper dc1-zookeeper:2181 --topic test-topic

EXAMPLE
^^^^^^^
./bin/kafka-run-class.sh kafka.tools.MirrorMaker --consumer.config config/mm.dc2.consumer.config --num.streams 2 --producer.config config/mm.dc2.producer.config --whitelist=".*"
./bin/kafka-run-class.sh kafka.tools.ConsumerOffsetChecker --group mirrormaker.dc1 --zookeeper zoo0000:2181


OPS MONITORING HOWTO
^^^^^^^^^^^^^^^^^^^^
  # Enable JMX upon java start
  kafka-server-start.sh:export JMX_PORT=9999
  kafka-run-class.sh:KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote=true
  kafka-run-class.sh:KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.port=9999 "
  service kafka restart ; netstat -pantu|grep 9999

  # Use jconsole(with GUI) or tjconsole(from console) to look at your options
  https://github.com/m-szalik/tjconsole
  [broker-srv1005 #] java -jar tjconsole-1.5-all.jar
  TJConsole> ? 
  TJConsole>connect 127.0.0.1:9999 
  TJConsole>use kafka<tab> ... kafka.server<tab> ...kafka.server:type=BrokerTopicMetrics,name= <tab> <etc etc etc etc> 
  TJConsole>use kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec 
  TJConsole>get 

https://github.com/jmxtrans/jmxtrans
- Make your .json. This is ugly as hell. Use git:llaursen/kafka/host.json.j2 as example, or google for stackdriver's jmxtrans kafka.json (incompatible with 0.8.2, incorrect mbean names and quotes usage. Only use as an example.). Also use TJConsole above in order to find interesting metrics and proper mbean metric names.
  [srv1005 /usr/share/jmxtrans]# ./jmxtrans.sh start kafka.json 
- tail -f /tmp/JMXTrans/kafkaStats/BytesInPerSec.txt or whatever 


MAINTENANCE
^^^^^^^^^^^
Normally if a kafka broker dies a horrible death, you would bring up a new one to replace it which **has the same broker.id as the failed box.** This way, once the new broker is back, the other brokers in the cluster (and zookeeper) will treat it like the old one and fully restore its state.

In the instance you would like to permanently remove a broker, you are going to have to run the kafka-reassign-partitions script in order to get all partitions off the thing prior to removal. kafka-manager is a good tool to use for this. You may also use airbnb's kafkat, or if you're a narcisist, you can use the command line json based kafka-reassign-partitions.sh tool.

In the case of adding a new broker, 0.8.2+ will automatically rebalance partitions amongst all brokers in a cluster if you have the config option enabled. I'm including an example here in the case that you would like to do it manually for some reason. In our example, p3r3 is a topic with...3 partitions and 3 replications:

  #If you don't have / haven't built your --reassignment-json-file, do below to generate one. Otherwise, skip to last command.
  #Create a json file which includes topics you want to rebalance
  > cat topics-to-move.json
  {"topics":
         [{"topic": "p3r3"},{"topic": "list_example"}],
  "version":1
  }
  #Run the tool to --generate a json line you need to use later
  #--broker-list includes your new broker(s), and excludes any broken one(s).
  ./kafka-reassign-partitions.sh --generate --broker-list "0,1,2" --topics-to-move-json-file topics-to-move.json --zookeeper srv1002:2181 
  #Look at the output. If it's doing what you want, put the final line into a file
  !! | tail -1 > my-generated.json
  #Now run the tool with --execute and --reassignment-json-file in place of generate and topics-to-move
  ./kafka-reassign-partitions.sh --execute --broker-list "0,1,2" --reassignment-json-file my-generated.json --zookeeper srv1002:2181
  #All this thing does is modify zookeeper, then kafka picks up the changes.
  #After all replication looks complete (hdd activity dies down, new brokers have expected disk space used, etc), run with --verify to check if all went accordingly
  #You may want to run kafka-preferred-replica-election.sh after this if your LEADER is not your PREFERRED replica.


COMMON ERRORS
^^^^^^^^^^^^^
**"failed due to Leader not local for partition|NotLeaderForPartitionException"** :: This usually just means that a producer/consumer tried to produce/consume to a broker which was not leader for that partition. These errors will occur when brokers get restarted, ISR's get shifted, partition reassignment happens, etc. etc. and can usually be ignored unless they come in high volume or repeat for longer than 5 seconds. Clients should use this error as a queue to re-request updated metadata to find a new leader. Note: You may also get this error if a metadata update request fails...


PERFORMANCE
^^^^^^^^^^^
**::Memory Related::**

kafkaServer-gc.log will let you know when you're hitting garbage collection:
  2015-04-29T13:48:02.610-0700: 89.811: [GC (Allocation Failure) 89.812: [ParNew: 279664K->48K(314560K), 0.0037317 secs] 284469K->4856K(1013632K), 0.0038937 secs] [Times: user=0.04 sys=0.00, real=0.00 secs]

Generally we want to **reserve a ton of our RAM for filesystem caching** as that is how kafka works, rather than giving a bunch of it to JVM. Still, lets try to give JVM an efficient amount such that garbage collection doesn't occur too often.

Connect to your kafka broker under load using jconsole and then click the Memory tab and wait a few seconds. The bars marked "Heap" in the bottom right are what you're wanting to pay attention to - CMS, Eden, and Survivor. 
- You generally want CMS to be low to nothing. This gets cleared out when ConcurrentMarkSweep runs.
- It's ok for Eden space to bounce around a lot
- If survivor space is often filling up, you need to allocate more memory to your heap. This is where you run into java.outofMemory errors.

You also want to pay attention to the GC time: text to see how long garbage collection is taking. ConcurrentMarkSweep is a very expensive operation, so it's important that it runs fast.

With kafka 0.8.2 and producer-perf-test running pushing around 400-500mbit (its advertised maximum on a 1gig connection), you'll generally fill 1gig of CMS every ~45mins (**no consumers**).

Note consumers have a large impact on memory usage. Do your memory tweaking both with and without consumers running. Note that if you're seeing a lot of rebalances in your consumer log, you probably need to increase the amount of memory you've given your consumer process.


**::Partition Rebalancing::**

Your producers might spew a bunch of these after adding/removing a producer or experiencing some sort of temporary outage on one/all of your brokers:
  [2015-04-29 14:18:44,139] WARN Produce request with correlation id 10556 failed due to [perf_test6p2r,0]: kafka.common.NotLeaderForPartitionException (kafka.producer.async.DefaultEventHandler)

You might see this in your controller.log:
  [2015-04-29 14:18:38,826] TRACE [Controller 1]: checking need to trigger partition rebalance (kafka.controller.KafkaController)

This is normal if you have recently had a broker shut down for a length of time, or have added a new broker, experienced a disruption, etc etc. Kafka is rebalancing partitions by possibly saying "hey (new|formerlyfailed) broker, you handle these partitions", setting as an ISR, waiting until it is in sync, and then promoting that broker to be leader for a certain partition. During this failover, if you want guaranteed delivery of messages, your producer must catch the non-fatal kafka.common.NotLeaderForPartitionException and pause publishing or consuming for several hundred ms. Kafka clients will auto retry to send 3 times with 100ms delay between retries before deciding to drop the message (default).

**::SO_SIZES::**

You may see socket.send.buffer.bytes & socket.receive.buffer.bytes in kafka's server.properties. I didn't see any performance increase/decrease moving these from 1MB -> 10MB when pushing 500Mbit x 3 producers -> 3 node cluster, no matter the buffer size. The limitation in this case appears to be the producer-perf-test suite.


KAFKA RELATED TOOLS/CLIENTS SETUP DEETS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**::flasfka::**

https://github.com/travel-intelligence/flasfka :: Expose kafka over python's simple web framework flask(http)

  yum install python-devel
  git clone https://github.com/travel-intelligence/flasfka
  python setup.py #DEPS WARN: This will grab both kafka and flask python modules

/etc/flasfka/conf.py:
  HOSTS=["srv1005:9092","srv1007:9092","srv1008:9092"]
  DEFAULT_GROUP="flasfka"
  CONSUMER_TIMEOUT=0.1
  CONSUMER_LIMIT=100

Don't forget to set your environment variable:
  export FLASFKA_CONFIG=/etc/flasfka/conf.py

/usr/lib/python2.7/site-packages/flasfka-0.0.1-py2.7.egg/flasfka/__init__.py:
  import logging
  logging.basicConfig()
  app.run(host='0.0.0.0') #Add to BOTTOM

Check your shit:
  /usr/bin/flasfka-serve & ; netstat -pantu|grep 5000
  curl http://localhost:5000/topic-name/


