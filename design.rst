Data Intensive Design
=====================

General
-------

Many applications need to:

- Store data so that they, or other applications, can find it again later (*databases*)
- Remember the result of an expensive operation, to speed up reads (*caches*)
- Allow users to search data by keyword or filter it in various ways (*search indexes*)
- Send a message to another process, to be handled asynchronously (*stream processing*)
- Periodically crunch a large amount of accumulated data (*batch processing*)

This section describes data systems - methods to achieve reliable, scalable and maintainable data systems.


                                    O
                                   /|\
                                    /\
                                    |
                                 +--v--+
                                 | API |
                                 +-----+             asynchronous tasks
                              client|req     +-------------------------------+
                                    |        |                               |
       +-----+  read req    +-------v--------++                              |
       |inmem<--------------+ Application Code+----------------+             |
       |cache| check-if-    +-------+---------+                |             |
       +--+--+ cached               |                          |search       |
          ^                         |                          |requests     |
          |                         |                          |             |
          |                         |                          |             |
          |                    +----v------+               +---v-----+       |
          |                    |           |               |         |       |
          |                    | Primary   |               |Full-text|       |
invalidate|                    | Database  |               |Index    |       |
or update |                    |           |               |         |       |
cache     |                    +---+-------+               +---^-----+       |
          |                        |                           |             |
          |                        |capture                    |             |
          |                        |change                     |             |
          |                        |data                       |         +---v--------+
          |              +---------v------------+ apply updates|         |Msg Queue   |
          +--------------+ Application Code     +--------------+         |            |
                         +----------------------+ to search index        +---+--------+
                                                                             |
                                                                             v
              Figure 1: Possible architecture for a data system

||

**Reliability:** Continuing to work correctly, even when things go wrong. Things going wrong are called *faults*, and systems that anticipate faults and can cope with them are said to be *fault tolerant*. Generally, fault tolerance is better than fault prevention, as prevention is impossible in many scenarios.

Hard disks have a mean time to failure (MTTF) of about 10 to 50 years. Thus on a storage cluster with 10,000 disks, we can expect an average of one disk to die per day.

Human error: leading cause of outages. Hardware/network faults: 10-25% of outages.

Well designed API's, admin interfaces, abstractions will encourage people to do the right thing. Any restrictiveness in these systems will encourage them to work around them.

Good stuff: Dev environments, automated unit testing, easy to roll back config changes, gradual rollouts, clear monitoring/metrics, good mgmt practices and training.

**Scalability:** If the system scales *in a particular way*, what are our options for coping with the growth?

Describe load: num of req's/sec, ratio of reads to writes on a db, num of simultaneously active users, hit rate on a cache...

Input req/sec might be small, while fan-out of that data might be huge. 

Twitter Eg1: tweet gets posted to a global collection of tweets. When a user requests home timeline, look up all the people they follow, find all recent tweets for each of those users, and merge them (sorted by time). Relational query might look like:

    SELECT tweets.*, users.* FROM tweets JOIN users ON tweets.sender_id = users.id 
    JOIN follows ON follows.followee_id = users.id 
    WHERE follows.follower_id = current_users

Twitter Eg2 (this is what they are doing as of November 2012): Maintain a cache for each user's home timeline - like a mailbo of tweets for each recipient user. When a user posts a tweet, look up all the people who follow that user, and insert the new tweet into each of their home timeline caches. The request to read the home timeline is then cheap, because its result has been computed ahead of time.

Twitter gets ~4.6k tweets/sec, that fans out (up to 31M followers per user) to per-user caches (this fan-out costs 345k writes/sec, or an avg of 75 followers per user). Others who are getting home timeline feed/using the api read these caches, at 300k reads/sec


Response Time
^^^^^^^^^^^^^
*response time*: the time between a client sending a request and receiving a response.

Reporting on an average response time (adding up all *n* response times and then dividing by *n*) is often inadequate, as it does not tell you how many users experienced a particular delay. Random additional latency could be introduced by a context switch, loss of a packet when using TCP, a GC pause, a page fault forcing a disk read, etc. As such, response times should optimally be represented as a distribution, using *percentiles*.

The *median*, where half of a users requests are served faster than, say, 200ms, and the other half are served slower, is known as *50th percentile* (aka *p50*). In order to figure out how bad your outliers are, you can look at higher percentiles: *95th, 99th,* and *99.9th* percentiles (p95, p99, p999). These are response time threshholds where 95, 99, or 99.9% of your responses are faster than that particular threshhold.

For example, if the 95th percentile response time is 1.5 seconds, that means 95 out of 100 requests take less than 1.5 seconds, and 5 out of 100 requests take 1.5s or more.

These percentiles can be very important...for example amazon has found that those *customers with the slowest requests are often those who have made many purchases*. They also observed that a *100ms increase in response time reduces sales by 1%*, and others report that a 1 second slowdown reduces a customer satisfaction metric by 16%.

On the other hand, optimizing for 99.99th percentile was deemed too expensive.


General Scaling
^^^^^^^^^^^^^^^

*scale-up*, get a more powerful machine. *scale-out*, distribute load across multiple machines. Distributing load across multiple machines is also known as a *shared nothing* architecture. A good architecture is a mixture of these.

An *elastic* system is good for unpredictable load changes, or cost savings around ebbs and flows in traffic. Manually scaled systems are simpler, and have fewer operational surprises.

When scaling out, it's easy to distribute stateless services across many machines. It's immediately much more complex to distribute a stateful service. For this reason, it is sometimes wise to keep your stateful database on a single node (scale up) until scaling costs are too high, or high-availability requirements force you to make it distributed.



