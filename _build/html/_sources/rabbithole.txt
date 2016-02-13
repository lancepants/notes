Rabbit Hole
===========

**"Describe exactly what happens when you type 'telnet google.com 80' at a bash prompt in as much detail as possible"** 

The above question (or a variant of it) is an extremely common interview question, with a nearly bottomless answer to it. This page attempts a reasonable answer.

Shell Interpretation
--------------------
- Shell interpreter takes in each item, separated by space, and saves it. In this case nothing fancy is going on, and bash might set ARG1 to google.com and ARG2 to 80
- Shell looks in its $PATH for an executable named telnet

Process Creation
----------------
- Shell calls fork(), passes procname and port arguments to it
- fork() system calls to sys_fork(), sys_fork() calls do_fork(), do_fork() does an alloc_pidmap to get a new PID
- do_fork() then calls copy_process() and passes the flags, stack, and registers used by the parent process, the parent process PID, and the newly allocated PID. do_fork() now waits.
- copy_process() does its thing by creating a duplicate set of stack and task_struct for the new process, and all pointers and whatnot to file descriptors, memory space, etc. used by the parent. Memory is not actually copied, a copy-on-write system is used
- Now, copy_process() calls copy_flags(), with a bit set to run exec() likely being in there
- The new task is then assigned to a processor, and control is passed back to do_fork() with a pointer to the new child
- The process isn't actually running at this point, so do_fork() calls the function wake_up_new_task on it. This places the new process in a run queue and wakes it up for execution
- do_fork() then returns the new PID value to bash
- The child in the meantime has been woken up and has ran exec() on telnet, passing it google.com and port 80, and replaced its memory space with whatever telnet wants. It might also have closed a pipe file descriptor that it inherited from the parent, off-handedly letting the parent know that exec has ran (parent watches the pipe for an EOF)

Telnet
------
- Now Telnet needs to do a DNS lookup.
- Telnet (or perhaps an underlying library that telnet calls to handle connections. Let's assume telnet does the work itself for this example) initializes an ‘addrinfo’ type struct called hints, which you can use to fill in some bits that getaddrinfo()'s resulting struct may not fill out (socktype, protocol etc) 
- Telnet then does a system call, getaddrinfo(), passing it a DNS name, and a protocol(eg:http) or a port number, and your hints struct that you just initialized
- getaddrinfo()'s main job is DNS resolution. It returns a struct with network info that telnet can use for resultant calls to socket() and connect() (more on this after dns resolution)


DNS Resolution
--------------
- Host looks in its cache for www.google.com (if it has a dns cache)
- Host looks in /etc/hosts (normally this order. Depends on your /etc/nsswitch.conf)
- Host asks its configured nameserver(s) where www.google.com is (AFAIK it's getaddrinfo() that does a connect() in the background to connect to this configured nameserver to query)

Nameserver
^^^^^^^^^^
- nameserver checks its cache
- (if nameserver not recursive) nameserver sends request to configured recursive nameserver 
- recursive nameserver has "hints" of the known address of root (top level domain) name servers, or explicit config entries for some
- recursive nameserver asks root nameserver for www.google.com, root nameserver passes back authoritative nameserver for .com
- recursive nameserver asks authoritative nameserver for .com for www.google.com, .com nameserver passes back auth nameserver for google.com
- recursive nameserver asks authoritative nameserver for google.com for www.google.com
- authoritative nameserver for google.com answers www.google.com = 147.0.2.3
- recursive nameserver passes back info to previous host or nameserver
- IP information passed back to getaddrinfo()

Socket Stuff
------------
- getaddrinfo() finished running, and passed back a struct with stuff like the resolved IP address, socktype, protocol, etc.
- Telnet now calls the socket() system call in order to get a socket file descriptor. Telnet passes socket() domaintype(ipv4 or 6), socket type (eg: sock_stream), and protocol (tcp, udp etc). You get a file descriptor back. sock_stream is the right choice in this case, as telnet uses TCP because telnet is designed to be a character type device.
- Telnet then calls connect(sockfd, dest.ip). The kernel will choose a local port and bind() for us

Destination Server
------------------
- Destination server has done the socket(); bind(); listen() dance when it started up, and is waiting for traffic.
- listen(socketfd, backlog) has a backlog...this is the number of connections allowed on the incoming queue. Connections will wait until the server accept()'s them.
- Destination httpd server hits accept(). Upon accepting a connection, a struct (type: sockaddr) is created with connection info (port, srchost, etc), a new socket is created, and a NEW file descriptor # is passed back to httpd. The original socket goes back to listening, while the new one is used for the new connection

TCP Handshake
-------------
1. SYN: Client sends a SYN packet to the server, which has its SEQ number set to random value A
2. SYN-ACK: In response, the server replies with a SYN-ACK. The acknowledgment number is set to one more than the received sequence number i.e. A+1, and the sequence number that the server chooses for the response packet is another random number, B.
3. ACK: Finally, the client sends an ACK back to the server. The sequence number is set to the received acknowledgement value i.e. A+1, and the acknowledgement number is set to one more than the received sequence number i.e. B+1

-Connection established. Now Telnet can do a send() and recv()

    char ASTERISKmsg = "Beej was here!";
    int len, bytes_sent;
    len = strlen(msg);
    bytes_sent = send(sockfd, msg, len, 0);



Further Work
------------
- Describe the path that a packet takes through the kernel and out the wire. How does the kernel know which device to use? How does that mapping work?
- Expand on accept() in destination server section
