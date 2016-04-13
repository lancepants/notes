.. _networking:

Networking
==========

.. _networking-tcp:

TCP
---
*IP* works by exchanging pieces of information called packets. A packet is a sequence of octets (bytes) and consists of a header followed by a body. The header describes the packet's source, destination and control information. The body contains the data IP is transmitting.

Due to network congestion, traffic load balancing, or other unpredictable network behavior, IP packets can be lost, duplicated, or delivered out of order. TCP detects these problems, requests retransmission of lost data, rearranges out-of-order data, and helps minimize network congestion to reduce the occurrence of the other problems. Once the TCP receiver has reassembled the sequence of octets originally transmitted, it passes them to the receiving application.

- Ordered & error checked delivery of data
- TCP waits for out-of-orders or retransmissions. This makes it unsuitable for live data (skype etc)
- Transmission Control Protocol accepts data from a data stream, divides it into chunks, and adds a TCP header creating a TCP segment. The TCP segment is then encapsulated into an Internet Protocol (IP) datagram, and exchanged with peers.
- The term TCP packet appears in both informal and formal usage, whereas in more precise terminology segment refers to the TCP Protocol Data Unit (PDU), datagram[4] to the IP PDU, and frame to the data link layer PDU

- A TCP segment has a header and a data section
- TCP header has: sport, dport, seq #, ack #, offset, reserv, flags (9 control bits), wsize, chksum, urg pointer, options, padding
- flags contains stuff like SYN, ACK(1=enable ack), RST(reset conn), FIN(no more data from sender)...etc
- The Seq number field has dual purpose. If SYN=1, then Seq# is set to the initial sequence number. The sequence number of the actual first data byte and the acknowledged number in the corresponding ACK are then this sequence number plus 1. In other words, Seq# doesn't increment until the data starts


TCP Connection Establishment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(server has a port binded and is listening. passive open.)
1. SYN: The active open is performed by the client sending a SYN to the server. The client sets the segment's sequence number to a random value (eg:222).
2. SYN-ACK: In response, the server replies with a SYN-ACK. The acknowledgment number is set to one more than the received sequence number i.e. 223, and the sequence number that the server chooses for the packet is another random number, 333.
3. ACK: Finally, the client sends an ACK back to the server. The sequence number is set to the received acknowledgement value (223 - yes, same as above), and the acknowledgement number is set to one more than the received sequence number i.e. 334

**Seq# Note:**
Seq#'s are used to identify each BYTE of DATA, not each tcp segment. So, if a sending computer sends a packet containing four payload bytes with a sequence number field of 100, then the sequence numbers of the four payload bytes are 100, 101, 102 and 103. When this packet arrives at the receiving computer, it would send back an acknowledgment number of 104 since that is the sequence number of the next byte it expects to receive in the next packet. This is called Cumulative Acknowlegement. 

.. _networking-mtu:

Maximum Transmission Unit (MTU)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
MTU is referenced by packet (and frame) based protocols like TCP and UDP in order to determine the maximum size of packet it should construct for communication over a given interface. Something called **Path MTU Discovery** (PMTUD) is used in order to discover this value.

In IPv4, this works by setting the *DF* (don't fragment) bit in the ip header of outgoing packets. Any device along the network path whose MTU is smaller than the packet will drop it and send back an ICMP *fragmentation needed* message containing its MTU. The source host reconfigures appropriately, and the process is repeated.

IPv6 works differently as it does not support fragmentation (nor the don't fragment option). Instead, the initial packet MTU is set to the same as the source interface, and if it hits a device along the path where the packet size is too large for its MTU setting, that device drops the packet and sends back an ICMPv6 *Packet Too Big* message which contains its MTU. The source then reconfigures its MTU appropriately, and the process is repeated.

If the path MTU changes lower along the path after the connection is set up, the process still does its thing. If the MTU changes to a higher value, PMTUD will eventually discover this (Linux performs another PMTD check every 10 minutes by default) and increase MTU accordingly.

Some firewall operators will blanket deny all ICMP traffic. This means that after a TCP handshake happens and the first packet is sent out with a larger MTU than something along the link can handle, the firewall blocks the ICMP reply and you end up with a "black hole" connection where the source keeps retrying to send data and some device along the path keeps dropping it, with a blocked response. Some PMTUD attempt to infer this problem and lower MTU size accordingly, but the lack of response could also just be due to congestion.

Some routers may work around this issue by changing the *maximum segment size* (MSS) of all TCP connections passing through links which have an MTU lower than the ethernet default of 1500. While an MTU is concerned with the total size of a packet, MSS only determines the TCP Segment (minus TCP header) size - typical default = 536 Bytes.

[TCP Packet[TCP Segment[IP datagram[Data link layer Frame]]]]
[UDP Datagram[UDP Segment[IP datagram[Data link layer Frame]]]]

Maximum Segment Size (MSS)
^^^^^^^^^^^^^^^^^^^^^^^^^
- Typically derived from getting MTU from data link layer
- Watch for specialized network hardware along your data path screwing with headers, adding shit and making the packet sizes weird. 
- Troubleshoot: you might want to decrease MTU size on the sender. Also wireshark along the data path if possible (sometimes not due to hardware owned by upstream)


TCP Windows
^^^^^^^^^^^
- TCP Receive Window is the amount of data that a computer can accept without acknowledging the sender. Its original maximum was 64KB, and that's what the field can still hold. Now there is an option called TCP Window Scale which specifies a byte shift on the original field in order to determine how many orders of magnitude higher than the original 64KB that a window size should be set to.
- Window size is determined during the 3 way handshake
- The throughput of a communication is limited by two windows: the congestion window and the receive window. The former tries not to exceed the capacity of the network (congestion control) and the latter tries not to exceed the capacity of the receiver to process data (flow control).
- "Bandwidth Delay Product" :: (bits/sec) * RTTms = BDP. If more than 64KB of data is "in flight", then a bit shift is in order to raise window size
- Some routers and packet firewalls rewrite the window scaling factor during a transmission. This causes sending and receiving sides to assume different TCP window sizes. The result is non-stable traffic that may be very slow.

TCP Timestamps
^^^^^^^^^^^^^^
- Same as seq# basically. Not normally based on system clock, just a random value.
- In the case that the tcp window size exceeds the number of possible sequence numbers (remember, each seq# is assigned to 4bytes of info), the tcp timestamp is used to determine whether a retransmitted packet is part of this 4GB segment, or the other.

TCP Flags
^^^^^^^^^
**URG**: Urgent flag says "process me immediately, before finishing the stream". An example is when TCP is used for a remote login session, the user can send a keyboard sequence that interrupts or aborts the program at the other end. These signals are most often needed when a program on the remote machine fails to operate correctly.

TCP Problems
^^^^^^^^^^^^
- TCP sucks At Wireless. Wireless links are known to experience sporadic and usually temporary losses due to fading, shadowing, hand off, and other radio effects. This causes incorrect congestion prediction, window scaling, etc. A congestion avoidance phase occurs where speed is compromised. There are new congestion control algorithms out there that attempt to perform better (vegas, westwood, veno, santa cruz etc)
- The application cannot access the packets coming after a lost packet until the retransmitted copy of the lost packet is received. This sucks for stuff that is live


UDP
---
- Lower overhead & reduced latency vs TCP
- Less complexity. Useful where no response is not a big deal
- 64KB max message size

Networking General
------------------

Read me: https://dougvitale.wordpress.com/2011/12/21/deprecated-linux-networking-commands-and-their-replacements/

OSI Model
  application							data
  presentation							data
  session							data
  transport     [end-to-end connections and reliability]	segments
  network       [path determination & logical addressing]	packets
  data link     [physical addressing (MAC & LLC)]		frames
  physical      [media, signal, binary transmission]		bits

PDNTSPA! or "All People Seem To Need Data Processing"

TODO
.. image media/networking-tcppacket.png

ARP
^^^
A protocol used to translate network-layer addresses (ie: ip addresses) to link-layer addresses (mac addrs).

Start using "ip n" (ip neighbour) instead of arp -a.

Devices which "share" a virtual IP may use gratuitous arp upon virtual IP migration in order to spam update switches and other connected devices with the new associated mac address.


Switching and Routing
---------------------
STP
^^^

- STP (spanning tree protocol) analyzes a network to ensure no looping can occur on networks with shitty design. It does this by designating a root bridge, finding root "ports" which are just paths, and then disabling all ports aside from the least cost path. Updates and such on link down, etc. Disable stp on host ports for faster no shutdown (dont have to wait for convergence)
- A broadcast storm can occur when switches are in a loop. Switch A is connected to B and C, B connected to A and C, etc etc. Host A on switch A makes a broadcast request. Switch A broadcasts this to B and C. B broadcasts this to C. C broadcasts this to A, and A thinks that this is a new broadcast request and so sends out another broadcast to B. Repeat

Private VLANs
^^^^^^^^^^^^^
PVLANs, also known as port isolation, are vlans that contain switchports which are restricted such that they can *only communicate with a given "uplink".* This means that in contrast to using regular VLANs, you can have two servers connected to the same switch who are on the same pvlan, unable to talk to each other without routing through the designated uplink first. This means that direct peer-to-peer traffic between peers on the same switch is blocked - any such communication must go through the uplink.

A PVLAN acheives this by dividing a VLAN (*Primary*) into sub-VLANs (*Secondary*). A regular VLAN has a single broadcast domain, while private VLAN partitions one broadcast domain into multiple smaller broadcast domains. Here's the breakdown:

- *Primary VLAN*: The original VLAN. Used to forward frames downstream to all Secondary VLANs.
- *Secondary VLAN*: These are configured with one of the following types:
  - *Isolated*: Any switchports associated with an Isolated VLAN can reach the primary VLAN, but not any other Secondary VLAN. Additionally, hosts associated with the same isolated VLAN cannot even reach each other. There can be multiple isolated VLANs in one private VLAN domain.
  - *Community*: Any switchports associated with a common community VLAN can communicate with each other and with the primary VLAN, but not with any other secondary VLAN. There can be multiple different community VLANs within one private VLAN domain.

There are mainly two types of ports in a Private VLAN: *Promiscuous* and *Host*. A Host port further divides into Isolated port, and Community port. From the above description, we can derive that an uplink or cross-connect to a router/firewall/other switch would be configured as Promiscuous, while ports going to physical servers would be configured as host ports in either isolated or community.

