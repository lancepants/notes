IPv6
====

THE BITS
--------
- ipv6 is 128 bits long

  1011010010100110100100110010010001010001001000011110100101000101110100110100100011010010100011111010100101101011010010

- This is split into 8 groups of 16 bits, with a : every 16 bits

  1011010010100110:1001001100100100:....

- Now convert to hex. One hex value is 4 bits

  1011 0100 1010 0110 : 1001 0011 0010 0100 : ...
   B    4    A    6   :  9    3    2    4

- So that's the first 32 bits of an ipv6 address
- Most of the time the network is a /64

STRIP ZEROS
-----------
- Let's say we have leading 0's in our hex address. These get stripped off. You can include them, but other stuff will strip them off:

  003C:B47C:028D... --> 3C:B47C:28D....

- Here's another example. A host address, and what it gets shortened to:

  2001:DB8:21:111:0:0:0:1/64 --> 2001:DB8:21:111::1/64

- Any time we have consecutive zeros eg: 0:0:0:0, these can get shrunk to just ::.
- The router/other sees just 5 groups of 16 bits defined, and assumes there are 3 groups of 0's in place of "::"
- **You can only do this once per address**. For example 2001:DB8:0:0:15:0:0:2 --> 2001:DB8::15::2 is invalid. You can only use a single set of :: here, does not matter which group


LINK LOCAL
----------
- Link local addresses are used to do ipv6 related orchestration/control messages. These **will not route past directly connected devices**, and cannot be used by nginx/mysql/whatever else.
- The link local address is required for IPv6 sublayer operations of the Neighbour Discovery Protocol, as well as for some other ipv6-based protocols including dhcpv6
- If it begins with **"FE80::"** then it is a link local address. Almost always subnetted /64.
- Simply doing an "int fa0/0 ; ipv6 enable" on an interface will cause the interface to automatically generate a link local address. SLAAC is used to generate the address (more on that later).
- Link local addresses can talk within the interface's broadcast domain

EUI64 ADDRESSING
----------------
- Here's my linux ipv6 eth0 link local address:

  fe80::f6ce:46ff:fe2d:38e6/64

- The host portion of that is f6ce:46ff:fe2d:38e6. So how is that generated? You may notice that it's pretty close to your MAC address, but not quite. 
- Your mac is only 48 bits, but we need 64 to fill up the hostID portion of the address. So, we inject FFEE into the middle of the 48 bits. So 24bits of mac addr, FFEE, then 24bits of mac addr

  f4:ce:46:2d:38:e6  --> f4:ce:46:FF:EE:2d:38:e6

- Additionally, we come along and flip the 7th bit. If it was a 0, it flips it to 1, and vice versa 0 to 1. This is to conform with some MAC address standard
  - The 7th bit in a mac address is the "universal" bit. If 0, it means that the address was IANA assigned. It's 1 if the mac address was locally changed by an administrator. Assigning your own link local address to like, F80::1, breaks this RFC rule. Who cares? Nobody. It's a stupid rule that overcomplicates things, and continues to generate arguments

  f4:ce:46:FF:EE:2d:38:e6  -->  f6:ce:46:FF:EE:2d:38:e6  -->  f6ce:46ff:fe2d:38e6

- This process is the same should you choose to IP your hosts using EUI64, does not just apply to link local addrs. SLAAC does this automagically for us
- EUI64 only works with /64's
- So, you can manipulate what your link local address is going to be by changing your mac address. Additionally, cisco routers allow you to specify what you want your ipv6 local address to be:

  int fa0/0
  ipv6 address fe80::1

- This is perfectly fine and you might want to use it for small network segments, like the points between routers, just so it's much more readable
- But if you do screw up, how are duplicate IPv6 addresses discovered? Covered in Neighbour Discovery section below.


GLOBAL ADDRESSING
-----------------
- Global as in publicly routable
- Currently, global addressing assignments are 2xxx::/7 and 3xxx::/7. You should be able to hit up your ISP for a global block in one of these ranges.
- Once you have your global network block, IP'ing your hosts works just the same as described in the LINK LOCAL section. You can rely on EUI-64 and SLAAC to generate the HostID portion of your device's ipv6 IP, or you can just specify it yourself.
- Your host can generate its HostID, but how does it know what network it is a part of? Read the SLAAC section to see how this is figured out. In short, upon network boot, it queries a multicast group that your router is a part of and your router passes back a router advertisement containing network information.


NEIGHBOUR DISCOVERY
-------------------
https://www.youtube.com/watch?v=O1JMdjnn0ao

- **ARP and Broadcasts were REMOVED in v6!** The replacement is "Neighbour Discovery Protocol" (NDP), which communicates via Multicast.
- NDP just wants to translate ipv6 addresses into MAC addresses, and stick those translations into its neighbors cache (like arp cache)
- So, since there is no arp broadcast packet that hits everyone, we are using Multicast to discover our neighbors instead. Multicast still hits everyone, but a device only has to fully de-encapsulate the multicast message if the frame is destined for a multicast group it cares about
- If a server or something wants to contact a remote ipv6 address does not exist in its NDP cache, a multicast ICMP packet of type "Neighbor Solicitation" (NS) is sent to a multicast address group IP. This solicitation contains your link local source address, your mac address, and the remote target ipv6 address.
  - Wait, what multicast address group? It uses something called "Solicited Node Multicast Address Group"
  - Whenever you assign an ipv6 address to a host (either link local or global), that host is going to join a special multicast group based on the last 24 bits of its HostID
  - The multicast group IP always starts with FF02::1:FF. So, if you ping a host with link local address FE80::200:AAFF:FEAA:AAA, it actually sends a multicast message to FF02::1:FFAA:AAAA (where AA:AAAA is the last 24 bits of the hostID). Only hosts which share the last 24 bits of hostID end up processing the request and answering
  - Additionally, every host joins multicast group address FF02::1. This is essentially your multicast "broadcast" address that everyone listens on
- Once the solicitation hits the remote device, it responds (Unicast, directly now, to the sender's link local address) with a "Neighbor Advertisement" (NA) saying hey that's me, here's my mac addr etc
- Entry is saved into neighbor cache with link local address mapped to L2 mac address of remote device
- Entry changes to status "STALE" in cache after 30 seconds if no further traffic happens


Duplicate Address Detection
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Let's say we are trying to assign address 3333::3 to an interface.
- The process above, where a neighbor solicitation is sent out to the solicited node multicast address group, occurs automatically prior to binding a new ipv6 address to an interface. So, send out a neighbour solicitation to multicast address group ff02::1:ff00:3 , which is where any device that might already have 3333::3 as its address would be listening. This solicitation has source address :: because we don't want to use a source address that might already be in use
- If no neighbor advertisement is received from a device that already has that address, the device will send out its own neighbor advertisement to FF02::1 (ie: everyone) that it now has that ipv6 address. It also sends a message to ff02::16 stating that it's joining the ff02::1:ff00:3 group.
- If trying to assign a duplicate address, the neighbor solicitation happens (source address ::, destination group ff02::1:ff00:3 for example, and local source address is the IP you're trying to set), and then a device that already has the address responds with a neighbor advertisement to ff02::1 with its source address 3333::3 and its info, etc. Your device then should fail Duplicate Address Detection (DAD) and not assign the address.


Summary So Far
--------------
- FE80: Link Local
- 2xxx: Global Unicast (on interwebs today)
- 3xxx: Global Unicast (on interwebs today)
- FFxx: Multicast


ROUTING and STATELESS ADDRESS AUTOCONFIGURATION (SLAAC)
-------------------------------------------------------
- When you enable ipv6 routing on a cisco (conf t; ipv6 unicast-routing), it will automatically join the multicast broadcast group FF02::2 ("all routers" multicast group). When a host doesn't know where to send its packets, it will query the FF02::2 group to look for routers, and your router should respond.
- Once you enable routing, your router (cisco anyways) will send out a **"router advertisement"** (RAs) to the all nodes multicast group FF02::1 saying "hey i'm a router! I have network 2001:DB8:21:111::/64 on this interface". It does this every 200 seconds
- So when a client boots up and starts up an ipv6 interface, it sends out a **"router solicitation"** to FF02::2. This triggers an immediate router advertisement, which the router sends out to FF02::1. The client receives the router advertisement and **reads in the ICMPv6 Option Prefix Information section of the packet** that its network prefix is 2001:DB8:21:111::/64. It then takes this prefix, **generates its own ipv6 EUI-64 address** (based on its mac), and then **sets its gateway for that interface to the source address of the router solicitation.**

- Let's say that the router's IP is fa80::1 and the host's MAC address is 88:88:88:88:88:88. The host would therefore generate the following IPv6 interfaces and default gateway:

  fe80::288:88ff:fe88:8888  Its link local address
  2001:db8:21:111::288:88ff:fe88:8888  Its EUI-64 generated global address
  fe80::1  The router solicitation source address as its default gateway

- Some OS's might even create an additional ipv6 address which is totally random, like 2001:db8:21:111:149f:30ab:5e81:6166 or something, and then use that to communicate to the internet with. This is so that remote servers on the internet can't track you by your specific EUI-64 ID. Each time you restart the network, a new random one is generated.


STATELESS DHCP
--------------
- So our clients can come up, generate their own IP, and get a default gateway. What about knowing which DNS servers it should be pointed at? Welp, turns out there's an "Option" flag in your router advertisement telling the client that there is more information available. The client does its config from the router advertisement and then queries the router for extra options. 
- On the router (cisco anyways):

  conf t ; ipv6 dhcp pool MYPOOL ; dns-server 2001:DB8:21:5555::5
  int fa 0/0 ; ipv6 dhcp server MYPOOL ; ipv6 nd other-config-flag

- In addition to the Option flag, there is also a "managed" flag available in the router advertisement. With this toggled, it tells the client not to generate its own EUI-64 address, and to instead get its IP from your DHCPv6 server. In the above example, all we're using dhcp for is to get a dns server


"PRIVATE" ADDRESSING
--------------------
- Non-routable addressing exists in IPv6. These addresses are called "Unique Local Addresses (ULA)" and exist in the range fc00::/7. 
- Since you're not using NAT (just don't. Read on, and also Google why NAT+ipv6 is a shitty idea), any host which has these addresses will not be able to communicate to the internet. They'll hit their internet gateway and on a properly configured router, get dropped. So, the only place you'd use these is perhaps as secondary IP's which are used internally between devices you own. This would simplify firewall rules.
- The caveat here is that **you're making the rest of your network more complex by using private, non-routable addressing**. Web/other proxies to the internet? Port forwarding/DNAT? Double NAT situations? UPnP, strict NAT modes screwing with gamers and other p2p protocols? "But I need the source IP for business intelligence" forcing direct routing traffic shenanigans back through a load balancer rather than your actual router/firewall/whatever? It's all awful. **Get rid of it.** Private addressing and NAT are a HACK. They're patchwork workarounds and they have abused us long enough that a lot of people have obvious signs of stockholm syndrome convincing themselves that they should continue with this broken, less secure, exception laiden model of networking. A lot of people are recommending not to use ULA's at all, and instead giving everything a global addr and then relying on iptables/ipfw/other and an upstream router or firewall to filter or vlan traffic. The filter rules would be very simple, and make a lot more sense than securing your network via an overly complicated private addressing design.
- Though ULA's are supposed to be non-internet-routable, the RFC states that they should actually be globally unique. Not sure why this is, as anything with this IP cannot communicate to the internet anyways due to a non-routable source address.
- Anyways, if you want to make a private network, you could start with the following:

  fc00:0000:0000:0001/64  -(shortened)->  fc00::1/64  #network address
  fc00::1:288:88ff:fe88:8888/64  #EUI-64 hostID generated from MAC 88.88.88.88.88.88


ANYCAST
-------
- Let's say you have two DNS servers hanging off of different routers, perhaps in different geographical locations.
- We want both DNS servers to have address 2345::9/64, so we assign that IP to both dns servers. 
- Now upstream of each of these, we give each of our upstream routers an ipv6 address if they don't have one already. Additionally, you enable some sort of routing protocol on that interface (eg: ospf) which is connected to your dns server. After that, you assign 2345::/64 to the interface as well ('ipv6 address 2345::/64 anycast' works on cisco routers. The 'anycast' token disables DAD). This causes ospf on each router to also advertize that it has the 2344::/64 network
- Once this is complete, any router listening for routing advertisements will see an advertised route for 2345::/64 and choose (based on routing protocol) which path is best (shortest, AS, ospf metric, etc)


BEST PRACTICES
--------------
- Give all your devices a globally addressable address and rely on firewalls for security/blocking outbound where needed
- Avoid ULA's (private addressing) as they will introduce unneeded network complexity, if not in your network today, then in the future
- You're generally going to get a /48 from your uplink provider. Your "leaves" or final network segments should be /64's. This allows EUI-64 to work. Pay attention to whatever subnetting you do in between those, you only have 16 bits left for VLAN'ing
- Use a /127 for p2p, and a /128 for loopback
- Manually configuring much simpler addresses (.1 - .f) for core routing gear/load balancers is a good idea for simplicities sake
- **Avoid "encoding" schemes**, where you use vlan numbers or former ipv4 addresses or building numbers/geo information in your address bits. These things change and will eventually screw up your structure. You don't need to avoid like the plague, but just be aware that these schemes tend to be wasteful and break, and they cause people to make sub-optimal future design decisions such that these schemes don't break.
- Rely on DNS and SLAAC. IP memorization sucks. Predictable IP's are awesome. Stop wasting time with this "find the next available IP from an inventory that might or might not be up to date, then ping/check router/switch arp cache to ensure the IP isn't already in use" and "make sure the inventory is updated after every single IP change" BS.


GOTCHAS
-------
- Tools like ip need the -6 argument to do shit. eg: ip -6 r
- With ping6 on linux you need to specify the interface you'd like to ping from (when pinging link-local addresses anyways). Eg: ping6 -I 172-br0 fe80::1
- No cisco, or have a linux or unix based router? "radvd" is the thing to use. Check it out
- On your linux/unix router, after you change your link local address (to something easier, like fe80::1) and remove your old one, restart radvd or it won't hand out adverts/gateway properly.
