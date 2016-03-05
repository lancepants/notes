Systems Administration
======================

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

Diagnostics
-----------
This records some lesser known or less fully understood utilities which should be used more often when diagnosing problems with a server.





Quickies
--------

Print the last column in each line of output:

  cat something | awk '{print $NF}'


