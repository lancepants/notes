Architecture
============

TODO:
- Note summary kleppmann's designing data intensive applications book
- Put "how would you design x" thoughts here where x is some big thing like facebook
- What was the hardest bug you've faced?

Design
------
Reference stackshare.io for ideas.
- (fb)Write about shared file systems which are read/written to from many servers.
- (fb)Write about distributed systems and different types of consistency models and where they are used

* (googs)How would you design Gmail?
* (googs)How do you best deal with processing huge amounts of data? (if you say map reduce, learn a ton about it)
* (fb)Outline a generic performant, scalable system. From frontend (lb's? or cluster-aware metadata like kafka) to backend (db's, storage, nosql options, etc). Remember networking as well: what features does a high performance network card supply - what can it offload? What should you tweak network wise for high bandwidth connections
* (fb)How would you design a cache API?

* (fb)How would you design facebook?
1) Define desired features, and split them into their own design. ie: photos, video, news feed, messenger, events

Video: Use GPU's to transcode streams to different quality levels

* (fb)How would you design a system that manipulates content sent from a client (eg: clean bad words in a comment post)?
For the clean bad words from a comment post, I would consider splitting the words in a comment post to a list (order matters here if we are to reconstruct the sentence, so can't sort or use a dict) and then iterating over them against a badwords hash/dict where the dict key is the badword. This would be O(n)+O(1), or an O(n) operation (this assumes that the hash function for the dict keys is sufficiently robust to make collisions uncommon, giving linear time O(1)).

If badwords is massive, you could consider keeping it sorted and then doing a binary search (O(log n)) against it when comparing words.

If the comment is huge or has many duplicate words and we want to prevent comparing them against the badwords more than once, you could consider splitting each word to a dict where the key is the word, and then doing a str.replace() on the original comment text if a badword match is found.

* Design the SQL database tables for a car rental database.
* How would you design a real-time sports data collection app?
* design a highly-available production service from bare metal all the way to algorithms and data structures. (eg: gmail, hangouts, google maps, etc.)


Broad/Architectural
Concerns with distributed architectures - moving to stateful microservices, or microservices that talk to other microservices in order to do their tasks. Start worrying about network latency, fault tolerance, message serialization, unreliable networks, asynchronicity, versioning, varying loads within the application tiers etc. etc. Moving to a cloud service shares some of these problems too.

http://blog.xebialabs.com/2014/12/31/8-questions-need-ask-microservices-containers-docker-2015/

Message queue's are useful because:
-They decouple a process, act as an intermediary. The advantages of this include scenarios such as traffic spikes, or when one side of the queue is offline for some reason. During a traffic spike, perhaps one process will get totally overwhelmed. This process can be decoupled so as not to take the entire system down. The MQ still exists, and allows the other side to pull off messages at its leisure without getting overwhelmed as well.
-A message queue can provide built-in message delivery guarantees, and also ordering guarantees. This saves you from having to build the logic into your application.
-A message queue acts as a buffer between two sides that may be operating at different speeds. This helps normalize speed. Additionally, analyzing the MQ's stats will give you an idea if one side is performing poorly.
-Finally, MQ's allow for asynchronous communication. This means that one side can push on a bunch of data and forget about it, the other side doesn't have to process it right away either.
