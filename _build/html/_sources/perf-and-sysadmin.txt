Performance and Troubleshooting
===============================
TODO:
- perftools, systemtap
- jconsole, java heap info
- bgregg stuff in general. Also ref http://techblog.netflix.com/2015/11/linux-performance-analysis-in-60s.html

General
-------
.. image:: media/performance-linux_observability_tools.png
   :alt: Linux Performance Observability Tools, bgregg
   :align: center

Python
------
Excellent: https://www.huyng.com/posts/python-performance-analysis

Runtime
^^^^^^^
  python3 -m cProfile wordfreq.py short-story.txt

Check out runsnakerun for visualization of cProfile output, pretty cool. www.vrplumber.com/programming/runsnakerun/
  python3 -m cProfile -o out.profile wordfreq.py short-story.txt ; python runsnake.py out.profile

Can also check out python visualization libraries that use graphvis.

Memory
^^^^^^
There is a module called memory_profiler that will output, line by line, how much memory your script uses:
  pip install -U memory_profiler
  pip install psutil #this is for better memory_profiler module performance
  vim freqgen.py #add @profile decorator above the function you're interested in
  python -m memory_profiler freqgen.py short-story.txt

