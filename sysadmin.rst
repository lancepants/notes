Systems Administration
======================

Network Troubleshoots
---------------------

tcpdump, tshark
^^^^^^^^^^^^^^^

tcpdump uses libpcap to filter, and libpcap compiles down to BPF (BSD Packet Filter). A readable filter expression like "ip and udp and port 53" would be compiled down to BPF bytecode, and then this filter program would be attached to the network tap interface. tcpdump would then pretty print the filtered packets received from the network tap. See this parsing in action by using the -d flag to tcpdump:

  tcpdump -p -ni eth0 -d "ip and udp"
  # some jt jf jeq blah blah bytecode

We just mentioned a network tap. tcpdump can open a network tap by requesting a **SOCK_RAW** socket, and after giving a few *setsockopts* calls, a filter can be set on your socket with **SO_ATTACH_FILTER**.

  mysock = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
  ...
  setsockopt(mysock, SOL_SOCKET, SO_ATTACH_FILTER, ...)


Memory
------

  free -m

See the -/+ buffers/cache value under the free column? That's how much RAM you have available. The value under "used" is how much is being currently used by the kernel for various things - mostly filesystem caching.

  top ; ps auxww
  cat /proc/<pid>/maps ; cat /proc/<pid>/smaps
  cat /proc/meminfo

top and ps have VIRT/VSZ for virtual mem, RSS/RES for resident, and (top) SHR for shared.

- **VIRT** stands for the virtual size of a process, which is the sum of memory it is actually using, memory it has mapped into itself (for instance the video cards’s RAM for the X server), files on disk that have been mapped into it (most notably shared libraries), and memory shared with other processes. VIRT represents how much memory the program is able to access at the present moment.
- **RES** stands for the resident size, which is an accurate representation of how much actual physical memory a process is consuming. (This also corresponds directly to the %MEM column.)
- **SHR** indicates how much of the VIRT size is actually sharable (memory or libraries). In the case of libraries, it does not necessarily mean that the entire library is resident. For example, if a program only uses a few functions in a library, the whole library is mapped and will be counted in VIRT and SHR, but *only the parts of the library file containing the functions being used will actually be loaded in and be counted under RES.*
- cat /proc/<pid>/maps and smaps as stated above for detailed per-process memory usage





Quickies
--------

- Find out what module a device is using

  lspci | grep Eth    # 84:00.0 Ethernet controller: Solarfla ....
  find /sys/ -name '*84:00*   # /sys/bus/pci/drivers/sfc/0000:84:00.0  ,  so, module "sfc"
  (alternately) lspci -nk


- Print the last column in each line of output:

  cat something | awk '{print $NF}'


