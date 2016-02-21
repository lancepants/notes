Architecture
============

TODO:
- Note summary kleppmann's designing data intensive applications book
- Put "how would you design x" thoughts here where x is some big thing like facebook

Broad/Architectural
Concerns with distributed architectures - moving to stateful microservices, or microservices that talk to other microservices in order to do their tasks. Start worrying about network latency, fault tolerance, message serialization, unreliable networks, asynchronicity, versioning, varying loads within the application tiers etc. etc. Moving to a cloud service shares some of these problems too.

http://blog.xebialabs.com/2014/12/31/8-questions-need-ask-microservices-containers-docker-2015/

Message queue's are useful because:
-They decouple a process, act as an intermediary. The advantages of this include scenarios such as traffic spikes, or when one side of the queue is offline for some reason. During a traffic spike, perhaps one process will get totally overwhelmed. This process can be decoupled so as not to take the entire system down. The MQ still exists, and allows the other side to pull off messages at its leisure without getting overwhelmed as well.
-A message queue can provide built-in message delivery guarantees, and also ordering guarantees. This saves you from having to build the logic into your application.
-A message queue acts as a buffer between two sides that may be operating at different speeds. This helps normalize speed. Additionally, analyzing the MQ's stats will give you an idea if one side is performing poorly.
-Finally, MQ's allow for asynchronous communication. This means that one side can push on a bunch of data and forget about it, the other side doesn't have to process it right away either.
