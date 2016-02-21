Linux Internals
===============

TODO:

- user vs system
- context switching
- CPU and IO schedulers, use tag ".. _linux-internals-scheduling:"

.. _linux-internals-systemcalls:

System Calls
------------
The kernel is the only program running in a special CPU mode called kernel mode, allowing full access to devices and the execution of privileged instructions. 

User processes run in user mode. These processes have a separate stack and registers (memory space) from kernel mode processes. These processes must request privileged operations from the kernel via system calls.

System calls are the primary mechanism by which user-space programs interact with the Linux kernel. The execution of privileged instructions in user mode causes exceptions, which are then handled by the kernel.

Popular system calls are open, read, write, close, wait, execve, fork, exit, and kill

An example with sys_read()
^^^^^^^^^^^^^^^^^^^^^^^^^^
my_app wants to access a storage device to read some info and then transfer that info to its memory space:

- main process passes its arguments to libc_read
- libc_read loads the specific system call number (in this case __NR_read) into the cpu's EAX register, as well as loads whatever other arguments (ie:what to read, the file descriptor of the file to read, etc) into other processor registers.
- libc_read then throws a special software interrupt which triggers an exception, which the kernel picks up and handles
- kernel code function system_call() is called, which has a look at the eax register to find out what system call to load
- sys_read() is called, which then uses the file descriptor it was passed to check for locks, and looks up a file struct which has a pointer to the function to call in order to handle that file type.
- sys_read() then does a read request to the device node driver function, which passes back information, and the process back up to userland is reversed

.. _linux-internals-pipes:

pipe(2)
^^^^^^^
https://brandonwamboldt.ca/how-linux-pipes-work-under-the-hood-1518/

Linux has an in-memory VFS called pipefs that gets mounted in kernel space at boot. The entry point to pipefs is the pipe(2) syscall. This system call creates a file in pipefs and then returns two file descriptors (one for the read end, opened using O_RDONLY, and one for the write end, opened using O_WRONLY).

Each unix process (except perhaps a daemon) has at least three standard POSIX file descriptors - STDIN, STDOUT, STDERR. In the case of unnamed pipes (eg: ls -la | grep blah), bash will:

* clone/exec grep
* call pipe(2) and get STDIN/STDOUT file descriptors back from the new pipe 
* call dup2() on the STDIN (fd[0]) of grep and the STDOUT (fd[1]) of the pipe
  * dup2() is a system call which duplicates two file descriptors, which will result in the two descriptors being able to be used interchangably (they refer to the same open file description, and thus share the file offset and file status flags. This means that, for example, if the file offset is modified by using lseek(2) on one of the descriptors, the offset is also changed for the other
* clone/exec ls -la
* call dup2() on the stdout (fd[1]) of ls and stdin (fd[0]) of the pipe

Named pipes, also known as FIFOs, work pretty much the same as unnamed pipes, except they stick around when programs are done using them.

Pipe size default is typically 64KB. When a pipe's buffer is full, a write(2) will block. If all file descriptors pointing to the read end of the pipe have been closed, writing to the pipe willr aise the SIGPIPE signal. If this signal is ignored, write(2) fails with error EPIPE.

When a pipe is empty, a read(2) will block. If there is nobody listening on the other end (all the file descriptors pointing to the write end of the pipe have been closed), then the pipe will return an EOF (ie: read(2) will return 0).


VFS
---
VFS works as an abstraction layer sitting between filesystems and system calls. By having this layer, a system call doesn't need to know how to communicate with all these different filesystems (ext3, ufs, zfs, nfs, /proc, /dev), and instead only communicates to VFS. VFS then communicates to the file system.

I/O Stack
---------
Application -> System Calls -> VFS -> File System -> Volume Manager -> Block Device Interface -> Target I/O Driver -> Host Bus Adapter Driver -> Disk Devices
It's also possible for the system call to skip straight to block device interface.

.. _kernel-signals:

Linux Signals
-------------
Signals are software interrupts. Kill sends a SIGTERM by default. The kernel delivers signals to target processes or process groups on behalf of an originating process, or on behalf of itself. If the originating process has the permissions to send a signal to another, the kernel forwards it on.

SIGHUP(1) - hangup - users terminal is disconnected somehow. Some daemons are programmed to reload their config and log files rather than close when they get this signal. If a process does not catch this signal, the default action of the parent is to close the process.
SIGINT(2) - interrupt - ctrl+c sends a sigint. SIGINT is nearly identical to SIGTERM, but "nicer." Interactive shells such as mysql may take it to mean "terminate current query" rather than terminate itself.
SIGKILL(9) - kill - forceful termination. Memory stripped. Cannot be ignored
SIGTERM(15) - Terminate. This asks the process to quit, go through its normal cleanup procedure
SIGSTOP(17,19,23) - Suspends a processes execution. Cannot be ignored. If you are experiencing some sort of intermittent socket/buffer full or backflow buildup related bug, SIGSTOP is a good way to reproduce the issue. File handles will be kept open.

Note that processes can ignore, block, or catch all signals except SIGSTOP and SIGKILL. If a process catches a signal, it means that *it includes code that will take appropriate action when the signal is received*. If the signal is not caught, the kernel will take the appropriate action for the signal.


Character vs Block Devices
--------------------------
Character (aka raw) devices provide unbuffered, sequential access of any I/O size down to a single character, depending on the device. An example of this would be a keyboard  or a serial port.

Block devices perform I/O in units of blocks, which are typically 512bytes. Blocks can be accessed randomly based on their block offset (location), which begins at 0 at the start of the block device.

/proc and /sys
--------------
procfs exposes runtime information & statistics of devices and processes, as well as allows you to change runtime variables on those devices and processes. Sysfs does the same thing, but provides a structure for this information. This structure is created by the kernel. Sysfs is intended as a replacement for procfs. All new stuff is expected to use sysfs rather than the unstructured dumping grounds of proc.

The sysfs (or /sys filesystem) was designed to add structure to the proc mess and provide a uniform way to expose system information and control points (settable system and driver attributes) to user-space from the kernel. Now, the driver framework in the kernel automatically creates directories under /sys when drivers are registered, based on the driver type and the values in their data structures.

Check number of caches available to cpu0 and the size of those caches:

  # grep . is same as cat /path/to/files*
  grep . /sys/devices/system/cpu/cpu0/cache/index*/size 
  # typical results: two 32k level 1 cache, 256k lvl2 cache, and 3MB lvl3 cache)


Process Management
------------------

Processes vs Threads
^^^^^^^^^^^^^^^^^^^^
Separate processes can not see each others memory. They have to communicate with each other via system calls (IPC). Threads share the same memory, so you lose the overhead. Unfortunately this also makes it easy for threads to step all over each other, with one thread perhaps changing a variable value without telling another thread. These are called Concurrency Problems.

It's fully possible for a process to create a bunch of threads to do stuff, and the kernel won't know about it. Its schedulers will keep treating the process as having one thread. This is bad for performance reasons. As such, there is a clone() system call (also used for process cloning) which allows registration and resource consideration within the kernel for a thread.


task_struct
^^^^^^^^^^^

Each process has a task_struct. This is a large structure which holds process data such as the state of execution, a stack, a set of flags, the parent process, the thread of execution (of which there can be many), and open files. The state variable is a set of bits that indicate the state of the task. The most common states indicate that the process is running or in a run queue about to be running (TASK_RUNNING), sleeping (TASK_INTERRUPTIBLE), sleeping but unable to be woken up (TASK_UNINTERRUPTIBLE), stopped (TASK_STOPPED), or a few others. The flags word defines a large number of indicators, indicating everything from whether the process is being created (PF_STARTING) or exiting (PF_EXITING), or even if the process is currently allocating memory (PF_MEMALLOC). The name of the executable (excluding the path) occupies the comm (command) field. The mm field represents the process's memory descriptors.

So, each userspace process gets its own task_struct, except init which has a statically defined struct called init_task. *These are collected into either a hash table (hashed by PID) or a circular doubly linked list*. The circular list is **ideal for iterating** through, such as a process scheduler would do. There is no head or tail to this list, so you can use the init_task struct as a reference point to iterate further.


Process Creation
^^^^^^^^^^^^^^^^

- Program calls fork() (actually clone() these days, but using fork() in this description)
- fork() system calls to sys_fork()
- sys_fork() calls do_fork()
- do_fork() does an alloc_pidmap to get a new PID
- do_fork() then calls copy_process and passes the flags, stack, and registers used by the parent process, the parent process PID, and the newly allocated PID
- copy_process consults with Linux Security Module (LSM) to see whether the current task is allowed to create a new task
- copy_process then calls dup_task_struct, which creates a new kernel stack, thread_info structure, and task_struct for the new process. The new values are identical to those of the current task. At this point, the child and parent process descriptors are identical.
- Now the child needs to differentiate itself from its parent. Various members of the process descriptor are cleared or set to initial values. Members of the process descriptor that are not inherited are primarily statistic information. The bulk of the data in the process descriptor is shared.
- Next, the child's state is set to TASK_UNINTERRUPTIBLE, to ensure that it does not yet run.
- Now, copy_process() calls copy_flags() to update the flags member of the task_struct. The PF_FORKNOEXEC flag, which denotes a process that has not called exec(), is set.
- Depending on the flags passed to clone(), copy_process() then either duplicates or shares open files, filesystem information, signal handlers, process address space, and namespace.
- The new task is then assigned to a processor, and control is passed back to do_fork() with a pointer to the new child
- The process isn't actually running at this point, so do_fork() calls the function wake_up_new_task on it. This places the new process in a run queue and wakes it up for execution
- do_fork() then returns the new PID value back on up through fork() to the caller
- **The parent process and the child process resume execution at the exact same spot.** fork() returns a PID > 0 to the parent process, such that it knows when it resumes execution that it is the parent. It will then likely call wait() in order to wait for the child to finish executing (or at least close all its related file descriptors, off-handedly letting the parent process know that the child ran successfully)
- The child process gets woken up and continues executing at the same spot as its parent, just after the fork() call. In contrast to the parent process, it gets a return PID of 0 from the fork() call, and hits an if pid == 0 block (true) which will then call execve() in order to replace the executable image of this child process

**tldr;** clone() is called, a new PID is generated as well as a new task_struct and other process-related info, flags are copied over to the new process's task_struct, the new task is assigned to a processor and then woken up and its PID is passed back to the parent process.

Example (NOTE: asterisks escaped (\*) due to markup formatting. Remove before running code):
  #include <unistd.h>
  #include <stdio.h>
  #include <fcntl.h>
  
  int main(void)
  {
    int pid = fork();
    // Child and Parent resume execution here
  
    if (pid == -1) {
      // fork threw an error
      fprintf(stderr, "Could not fork process\n");
      return -1;
    } else if (pid == 0) {  
      // retcode 0 means this is a child process
      fprintf(stdout, "Child will now replace itself with ls\n");
  
      // Setup the arguments/environment to call
      char \*argv[] = { "/bin/ls", "-la", 0 };
      char \*envp[] = { "HOME=/", "PATH=/bin:/usr/bin", "USER=derp", 0 };
  
      // Call execve(2) which will replace the executable image of this
      // process
      execve(argv[0], &argv[0], envp);
  
      // Execution will never continue in this process unless execve returns
      // because of an error
      fprintf(stderr, "Oops!\n");
      return -1;
    } else if (pid > 0) {
      // retval greater than 0, we are the parent process
      int status;
  
      fprintf(stdout, "Parent will now wait for child to finish execution\n");
      wait(&status);
      fprintf(stdout, "Child has finished execution (returned %i), parent is done\n", status);
    }
  
    return 0;
  }


Process Scheduling
^^^^^^^^^^^^^^^^^^
The scheduler maintains lists of task_struct's. Each list has a different priority number. task_struct's are placed in each list based on loading and prior process execution history, along with other factors depending on which process scheduler you're using.


Process Destruction
^^^^^^^^^^^^^^^^^^^

- User space calls exit(), which makes a sys_exit() system call, which calls do_exit()
- do_exit() sets the PF_EXITING flag in the processes task_struct, which tells the kernel to avoid manipulating this process while it's being removed
- do_exit() makes a series of calls. exit_mm to remove memory pages, exit_notify to notify the parent process and other things, and more?
- Finally, the process state is changed to PF_DEAD in its task_struct and the schedule function is called to select a new process to execute
- release_task is called which will reclaim memory that the process was using
