
Coding:


Quickies
--------
Make immutable, can't delete this file:
chattr +i filename

Special file being a douche to rm? eg: $!filename, -filename, 'filename-
ls -i    #list by inode
find . -inum 1234 -exec rm {} \;


Questions
---------
- Files, inodes, filesystems...how do they work? What are file descriptors? what are semaphores and how are they used?
- How are cookies passed in the HTTP protocol?
- How does traceroute work? Uses ICMP and uses gradually increasing TTL numbers to elicit a response from routers at each hop. Each router decrements the counter and if zero, will return an answer. The client keeps incrementing the counter in successive packets 'till it reaches its intended destination. The TTL counter exists in the IP header.

Google Glassdoor
^^^^^^^^^^^^^^^^
- Rank the following in terms of speed: access a register, access main memory, perform a context switch, hd seek time
- What information is contained in a file inode?
- Research possible problems with adding two integers of arbitrary size
- Common q about TCP path and MTU discovery
- Research null routing ("black hole connection")
- How would you design a real-time sports data collection app?
- How do you best deal with processing huge amounts of data? (if you say map reduce, learn a ton about it)
- Do a regex to get phone numbers out of a contacts.txt from google docs
- Which system call returns inode information? (study all common system calls and know them)
- What signal does the "kill" command send by default
- Describe a TCP connection setup
- design a highly-available production service from bare metal all the way to algorithms and data structures. (eg: gmail, hangouts, google maps, etc.)
- What happens when you type 'ps' (shell word splitting, searching PATH, loading dynamic libs, argument parsing, syscalls, /proc, etc. expand)
- what is the worst case time for a quicksort?
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
(googs)how would you design Gmail.
(fb)Outline a generic performant, scalable system. From frontend (lb's? or cluster-aware metadata like kafka) to backend (db's, storage, nosql options, etc). Remember networking as well: what features does a high performance network card supply - what can it offload? What should you tweak network wise for high bandwidth connections
(fb)How would you design a cache API?
(fb)How would you design facebook?
Design the SQL database tables for a car rental database.


Coding Questions
----------------
- Write the "tail" program, in python, on the whiteboard.
-(googs)Implement a hash table
-(googs)Remove all characters from string1 that are contained in string2
-(googs)implement quicksort. Determine its running time.
-(googs)Given a numerym (first letter + length of omitted characters + last letter), how would you return all possible original words? E.G. i18n the numeronym of internationalization
-(googs)Find the shortest path between two words (like "cat" and "dog), changing only one letter at a time.
-(googs)Reverse a linked list
-(googs)Write a function that returns the most frequently occurring number in a list
(fb)re-implement 'tail' in a scripting language
(fb)Battleship game: write a function that finds a ship and return its coordinates.
(fb)Write a script to ssh to 100 hosts, find a process, and email the result to someone
   for i in {1..100} ; do ssh user@host${i} "ps -ef|grep blah|grep -v grep|mail -s "This is the subject" user@myemail.com" ; done
(fb)Write a function to sort a list of integers like this [5,2,0,3,0,1,6,0] in the most efficient way (look up sorting algorithms)
(fb)Given a sentence convert the sentence to the modified pig-latin language: Words beginning with a vowel, remove the vowel letter and append the letter to the end. All words append the letters 'ni' to the end. All words incrementally append the letter 'j'. i.e. 'j','jj','jjj', etc... (what's the last part mean? append j's incrementally, what?)
(fb)take input text and identify the unique words in the text and how many times each word occurred. Edge cases as well as performance is important. How do you identify run time and memory usage?
(fb)build a performance monitoring script, adding more features and improving efficiency as you go
(fb)For a given set of software checkins, write a program that   will determine which part along the branch where the fault lies. 
 -So we assume we already have a list of git revisions, and once a certain revision gets hit everything after it fails
 -Do a binary search in order to determine where the build starts breaking. Ie: pick the middle number, do a checkout, build, if fail then do another binary search in the middle of startrevision and failedrevision-1. If success, then do another binary search between successrevision+1 and finalrevision..etc etc. Do this until you find that failedrevision-1=a successful revision
(fb)Given a list of integers, output all subsets of size three, which sum to zero. (wtf? http://www.glassdoor.com/Interview/Given-a-list-of-integers-output-all-subsets-of-size-three-which-sum-to-zero-QTN_580995.htm )
(fb)Given a list of integers which are sorted, but rotated   ([4, 5, 6, 1, 2, 3]), search for a given integer in the list. 
 -Think of the array as two separate lists. If number we're searching for is less than or equal to the last number in the array (3 in this case), then cut array in half and do a binary search on just that half until number is found
(fb)Write a frequency list generator! Do one attempt, then try to make it more efficient. Good problem to test performance with. Have it output the top 10 words or something.

    For above questions, elaborate on theoretical best performance. Talk about 
    memory vs CPU usage. Talk about whether certain system calls take more 
    resources than others. How long it takes to: access a register, access main 
    memory, perform a context switch, hd seek time
