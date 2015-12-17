.. _interview:

Interview Material
==================

Questions
---------
- Files, inodes, filesystems...how do they work? What are file descriptors? 
**Filesystems, inodes, file descriptors**: Described in :ref:`filesystems`

- What are semaphores? What is a mutex? What's the difference between the two?
A semaphore is best described as a signaling mechanism, but could also be described as a type of lock. A semaphore is an object that contains a (natural) number, on which two modifying operations are defined. One operation, V, adds 1 to the number. The other operation, P, removes 1. Because the natural number 0 cannot be decreased, calling P on a semaphore containing 0 will block the execution of the calling process/thread until some other thread comes along and calls a V on that semaphore. You may create a semaphore with more than one "slot" available (ie: s(6)). As such, semaphores can be used to restrict acess to a certain resource to a maximum (but variable) number of processes.

A mutex is a locking mechanism which helps multiple tasks serialize their access to a shared resource. It's simply some function or object you call prior to performing a block of code on some shared resource. Your first call sets a locked flag, then you run your code, and then your second call to the mutex releases the lock.

You might think of a semaphore or a mutex as a key to a bathroom. One key, one door works well for a mutex or a semaphore(1). But above we mentioned semaphores can count higher than one...so one key for six bathrooms. A mutex will not scale in this scenario as it would block each time 1/6 resources are used. A semaphore will allow 6 people to use the bathrooms at once, but it has no idea which bathroom is free at which time. What you end up needing is a separate mutex for each resource regardless. 

Because of this, you should not be relying solely on semaphores for locking - in fact, you really should only be using semaphores for simple signaling. For example, have a semaphore for power button which your display subscribes to (semaPend(sem_pwr_button); //wait for signal), such that when the power button is hit, a post (V, increment, semaPost(sem_pwr_button); //send the signal)) is sent and your display thread then unblocks and performs some_code. Another use could be naive throttling: only allow 3 threads to access a database at once.


- How are cookies passed in the HTTP protocol?
The server sends one of these in its response header (square brackets optional):
    Set-Cookie: <em>value</em>[; expires=<em>date</em>][; domain=<em>domain</em>][; path=<em>path</em>][; secure]

Note that "value" above is a string, and is almost always in a format like this: **key=value** , and is usually enforced as such.

And if the client accepts the cookie write, it sends this in its next request header:
    Cookie: name=value

- How does traceroute work? 
ICMP packets are sent, with the initial packet having a TTL of 0 and each consecutive packet having its TTL incremented by one. This elicits a response along each hop of a network path. The TTL count exists in the IP header.

Google Glassdoor
^^^^^^^^^^^^^^^^
- Rank the following in terms of speed: access a register, access main memory, perform a context switch, hd seek time
1 Register. 1 or 2 cycles. Smallest and fastest memory on a system. A compiler will typically allocate registers to hold values retrieved from main memory.
2 Perform a context switch (which type? assuming thread switch). 30-60 cycles best case.
3 Access main memory. NUMA local: 100 cycles NUMA remote: 300 cycles for no/normal congestion
4 HD seek time. A typical hdd needs anywhere from 2.5ms to 6.5ms to seek, depending on rotational speed (2ms=15k). Arm movement (stroke/track-to-track) takes anywhere from 0.2 to 1ms. SSD seek time is around 0.08-0.16ms

**Context Switch:** The process of storing execution state of a process or thread so that execution can be resumed from the same point at a later time.

    "Context Switch" can mean several different things, including: thread switch (switching 
    between two threads within a given process), process switch (switching between two 
    processes), mode switch (domain crossing: switching between user mode and kernel mode 
    within a given thread), and more. 

Which type of context switch you're talking about can mean a very different performance costs. For example, a context switch pausing one thread and the cpu scheduling another where each thread is not sharing memory (separate working sets) could dirty the cpu cache if there is not enough space to hold both thread's memory or the new thread fills the cache with new data. The same is true for processes. Additionally, if two processes share the same working set of memory and one is context switched out and another is scheduled in on a different core, it does not have access to the same cache/working set without a NUMA hop or a trip to main memory.

http://blog.tsunanet.net/2010/11/how-long-does-it-take-to-make-context.html



- What information is contained in a file inode?
**Filesystems, inodes, file descriptors**: Described in :ref:`filesystems`



- How is MTU size determined?
MTU is referenced by packet (and frame) based protocols like TCP and UDP in order to determine the maximum size of packet it should construct for communication over a given interface. Something called **Path MTU Discovery** (PMTUD) is used in order to discover this value.

In IPv4, this works by setting the *DF* (don't fragment) bit in the ip header of outgoing packets. Any device along the network path whose MTU is smaller than the packet will drop it and send back an ICMP *fragmentation needed* message containing its MTU. The source host reconfigures appropriately, and the process is repeated.

IPv6 works differently as it does not support fragmentation (nor the don't fragment option). Instead, the initial packet MTU is set to the same as the source interface, and if it hits a device along the path where the packet size is too large for its MTU setting, that device drops the packet and sends back an ICMPv6 *Packet Too Big* message which contains its MTU. The source then reconfigures its MTU appropriately, and the process is repeated.

If the path MTU changes lower along the path after the connection is set up, the process still does its thing. If the MTU changes to a higher value, PMTUD will eventually discover this (Linux performs another PMTD check every 10 minutes by default) and increase MTU accordingly.

Some firewall operators will blanket deny all ICMP traffic. This means that after a TCP handshake happens and the first packet is sent out with a larger MTU than something along the link can handle, the firewall blocks the ICMP reply and you end up with a "black hole" connection where the source keeps retrying to send data and some device along the path keeps dropping it, with a blocked response. Some PMTUD attempt to infer this problem and lower MTU size accordingly, but the lack of response could also just be due to congestion.

Some routers may work around this issue by changing the *maximum segment size* (MSS) of all TCP connections passing through links which have an MTU lower than the ethernet default of 1500. While an MTU is concerned with the total size of a packet, MSS only determines the TCP Segment (minus TCP header) size - typical default = 536 Bytes.

[TCP Packet[TCP Segment[IP datagram[Data link layer Frame]]]]
[UDP Datagram[UDP Segment[IP datagram[Data link layer Frame]]]]

Also reference: :ref:`networking-mtu`


- Which system call returns inode information? (study all common system calls and know them)
**Kernel - System Calls**: :ref:`kernel-systemcalls`


- What signal does the "kill" command send by default
Kill sends a SIGTERM by default. Note that processes can ignore, block, or catch all signals except SIGSTOP and SIGKILL. If a process catches a signal, it means that *it includes code that will take appropriate action when the signal is received*. If the signal is not caught, the kernel will take the appropriate action for the signal.

* SIGHUP is useful, most applications use this as an indication to reload their configuration without terminating themselves.
* SIGINT is sent when you ctrl-c something. It is intended to provide a mechanism for an orderly, graceful shutdown of the foreground process. Interactive shells (mysql, other) may take it to mean "terminate current query" rather than the whole process.
* SIGQUIT signals a process to terminate and do a core dump


- Describe a TCP connection setup
Look here: :ref:`networking-tcp`


- What happens when you type 'ps' (shell word splitting, searching PATH, loading dynamic libs, argument parsing, syscalls, /proc, etc. expand)
A variant of "the rabbit hole" question. :ref:`rabbithole`


- what is the worst case time for a quicksort?
Depends on your pivot. Look here: :ref:`algorithms`

- What is the maximum length of a binary tree? ("n, because it could be unbalanced")

- What is the theoretical best trans-continental round-trip ping time?
Light travels at just below 300,000KM/sec. Light travels through fiber around 30% slower, so 210,000KM/sec. London to NYC is about 5500KM. So, 5500/210000 = 0.026, or 26ms. Routers/switches only add microseconds of delay, so being generous, add 1ms total for both sides. So RTT = around 53ms. Verizon consistently sees 72ms between london and nyc in the real world.

- How do you solve a deadlock?
- Difference between processes and threads
- What is a socket
- What is a transaction (db) - expand
- What algorithm does python's .sort() use

Facebook Glassdoor
^^^^^^^^^^^^^^^^^^
- What is a filesystem, how does it work?
 
- What is a socket file? What is a named pipe?  
-     (RobertL: Data written to a pipe is buffered by the kernel until it is read from the pipe. That buffer has a fixed size. Portable applications should not assume any particular size and instead be designed so as to read from the pipe as soon as data becomes available. The size on many Unix systems is a page, or as little as 4K. On recent versions of Linux, the size is 64K. What happens when the limit is reached depends on the O_NONBLOCK flag. By default (no flag), a write to a full pipe will block until sufficient space becomes available to satisfy the write. In non-blocking mode (flag provided), a write to a full pipe will fail and return EAGAIN.)
 
- What is a signal and how is it handled by the kernel?
- What is a zombie process? How and when can they happen?
- What does user vs system cpu load mean?
- Difference between cache's and buffers?
- How can disk performance be improved?
- How would you design a system that manipulates content sent from a client (eg: clean bad words in a comment post)?
- Explain in every single step about what will happen after you type "ls (asterisk-symbol-redacted)" or "ps" in your terminal, down to machine language
- Suppose there is a server with high CPU load but there is no process with high CPU time. What could be the reason for that? How do you debug this problem?
  -Typically this is due to very short lived processes. (look up how to detect this). Also, does a process in high IOWait have an associated high cpu usage?
- What happens when a float is cast to/from a boolean in python?
- Given a database with slow I/O, how can we improve it?
  -Profile the thing to see where it's slow (expand)
  -indexing (expand)
  -disk optimisations (expand)
- What options do you have, nefarious or otherwise, to stop   people on a wireless network you are also on (but have no admin rights to) from hogging bandwidth by streaming videos?
  -discover their mac address (wifi raw mode? expand), create another interface and assign their mac address as your own, make script to forever perform gratuitous ARP until offender gets annoyed at poor performance and stops using internet. (might also just be able to do arping -U ip.addre.s.s & echo 1 > /proc/sys/net/ipv4/ip_nonlocal_bind http://serverfault.com/questions/175803/how-to-broadcast-arp-update-to-all-neighbors-in-linux) 
  -If you can gain access to wifi router, ban their mac or set QoS if available
  -(expand)
- How exactly does the OS transfer information across a pipe?
- What problems are you going to run into when doing IPC (pipes, shared memory structures)?
- what is "file descriptor 2"
  -STDERR apparently?
- What's the difference between modprobe and insmod?


Study Topics
------------
Brush up on RAID
quick brush up on more complicated regex
learn the particulars of ssh
core system functionality such as I/O buffering
SMTP
(googs)Prepare for Hashmap/hashtable questions
(googs)Understand how job scheduling is handled in the most recent iterations of the kernel
(googs)Know your signals
(googs)Study up on algorithms and data structs
(googs)Study the book "Cracking the Coding Interview" for several weeks prior to interviewing. practice "whiteboarding" your code
(fb)Review DNS, TCP, HTTP, system calls, signals, semaphores, complete paths (ie: telnet blah.com 80), boot process (incl UEFI)
(fb)Refresh CCNA related knowledge, TCPDump commands (memorize syntax, memorize basic "listen"), ipv6 notes, load balancing types, load balancer failover modes & how VIP mac addr changes (gratuitous/unsolicited ARP), direct routing vs NAT, jumbo frames, MTU size, fragmentation and when it can occur, what a packet looks like
(fb)Review systemtap, perftools, sar(sysstat), and other options
(fb)Write about shared file systems which are read/written to from many servers.
(fb)Write about distributed systems and different types of consistency models and where they are used


Design
------
* (googs)How would you design Gmail?
* (googs)How do you best deal with processing huge amounts of data? (if you say map reduce, learn a ton about it)
* (fb)Outline a generic performant, scalable system. From frontend (lb's? or cluster-aware metadata like kafka) to backend (db's, storage, nosql options, etc). Remember networking as well: what features does a high performance network card supply - what can it offload? What should you tweak network wise for high bandwidth connections
* (fb)How would you design a cache API?
* (fb)How would you design facebook?
* Design the SQL database tables for a car rental database.
* How would you design a real-time sports data collection app?
* design a highly-available production service from bare metal all the way to algorithms and data structures. (eg: gmail, hangouts, google maps, etc.)

Coding Questions
----------------

Google Glassdoor
^^^^^^^^^^^^^^^^
- Implement a hash table
- Remove all characters from string1 that are contained in string2
- implement quicksort. Determine its running time.
- Given a numerym (first letter + length of omitted characters + last letter), how would you return all possible original words? E.G. i18n the numeronym of internationalization
- Find the shortest path between two words (like "cat" and "dog), changing only one letter at a time.
- Reverse a linked list
- Write a function that returns the most frequently occurring number in a list
- Do a regex to get phone numbers out of a contacts.txt file

Facebook Glassdoor
^^^^^^^^^^^^^^^^^^
- re-implement 'tail' in a scripting language
- Battleship game: write a function that finds a ship and return its coordinates.
- Write a script to ssh to 100 hosts, find a process, and email the result to someone
- or i in {1..100} ; do ssh user@host${i} "ps -ef|grep blah|grep -v grep|mail -s "This is the subject" user@myemail.com" ; done
- Write a function to sort a list of integers like this [5,2,0,3,0,1,6,0] in the most efficient way (look up sorting algorithms)
- Given a sentence convert the sentence to the modified pig-latin language: Words beginning with a vowel, remove the vowel letter and append the letter to the end. All words append the letters 'ni' to the end. All words incrementally append the letter 'j'. i.e. 'j','jj','jjj', etc... (what's the last part mean? append j's incrementally, what?)
- take input text and identify the unique words in the text and how many times each word occurred. Edge cases as well as performance is important. How do you identify run time and memory usage?
- build a performance monitoring script, adding more features and improving efficiency as you go
- For a given set of software checkins, write a program that   will determine which part along the branch where the fault lies. 
 -So we assume we already have a list of git revisions, and once a certain revision gets hit everything after it fails
 -Do a binary search in order to determine where the build starts breaking. Ie: pick the middle number, do a checkout, build, if fail then do another binary search in the middle of startrevision and failedrevision-1. If success, then do another binary search between successrevision+1 and finalrevision..etc etc. Do this until you find that failedrevision-1=a successful revision
- Given a list of integers, output all subsets of size three, which sum to zero. (wtf? http://www.glassdoor.com/Interview/Given-a-list-of-integers-output-all-subsets-of-size-three-which-sum-to-zero-QTN_580995.htm )
- Given a list of integers which are sorted, but rotated   ([4, 5, 6, 1, 2, 3]), search for a given integer in the list. 
 --Think of the array as two separate lists. If number we're searching for is less than or equal to the last number in the array (3 in this case), then cut array in half and do a binary search on just that half until number is found
- Write a frequency list generator! Do one attempt, then try to make it more efficient. Good problem to test performance with. Have it output the top 10 words or something.

    For above questions, elaborate on theoretical best performance. Talk about 
    memory vs CPU usage. Talk about whether certain system calls take more 
    resources than others. How long it takes to: access a register, access main 
    memory, perform a context switch, hd seek time

Quickies
--------
Make immutable, can't delete this file:
    chattr +i filename

Special file being a douche to rm? eg: $!filename, -filename, 'filename-
    ls -i    #list by inode
    find . -inum 1234 -exec rm {} \;
