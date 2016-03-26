OS Theory
=========

General
-------

More on each of these later.

System Calls
^^^^^^^^^^^^
An application typically calls functions in a library - for example, the *C library* - that in turn rely on the system call interface to instruct the kernel to carry out tasks on the application's behalf. When an application executes a system call, we say that the *kernel is executing on behalf of hte application*. Furthermore, the application is said to be *executing a system call in kernel-space*, and the kernel is running in *process context*.

Interrupts
^^^^^^^^^^
The kernel manages the systems' hardware. When hardware wants to communicate with the system, it issues an *interrupt* that literally interrupts the processor, which in turn interrupts the kernel. A number identifies interrupts and the kernel uses this number to execute a specific *interrupt handler* to process and respond. 

For example, as you type, the keyboard controller issues an interrupt to let the system know that there is new data in the keyboard buffer. The kernel notes the interrupt number of the incoming interrupt and executes the appropriate interrupt handler. The interrupt handler processes the keyboard data and lets the keyboard controller know it is ready for more data.

In linux, the interrupt handlers do not run in a process context - they run in a special *interrupt context* that is not associated with any process. This special context exists solely to let an interrupt handler quickly respond to an interrupt, and then exit.

Contexts
^^^^^^^^

Contexts represent the bredth of the kernel's activity. In linux, we can generalize that each processor is doing exactly one of three things at any given moment:

- In user-space, executing user code in a process
- In kernel-space, in process context, executing on behalf of a specific process
- In kernel-space, in interrupt context, not associated with a process context, handling an interrupt

This list is inclusive! Even "idle" means the kernel is executing an *idle process* in process context in the kernel.

                                         +---------+
        +-------+  +-------+   +-------+           |
        |       |  |       |   |       |           |
        |App1   |  | App2  |   | App3  |           | User Space
        |       |  |       |   |       |           |
        |       |  |       |   |       |           |
        |       |  |       |   |       |           |
        |       |  |       |   |       | +---------+
        |       |  |       |   |       | +--------+
        |       |  |       |   |       |          |
        +---+---+  +----+--+   +---+---+          |
            |           |          |              |
    +-------v-----------v----------v-------+      |
    |                                      |      |
    |      System Call Interface           |      |
    |                                      |      |
    +---+-----------+-----------------+----+      |  Kernel Space
        |           |                 |           |
        |           |                 |           |
    +---v-----------v-------+ +-------v----+      |
    |  Kernel Subsystems    | |            |      |
    |                       | |            |      |
    +-----------------------+ |            |      |
    +-------------------------+            |      |
    |                                      |      |
    |                                      |      |
    |            Device drivers            |      |
    |                                      |      |
    +---+--------+--------+------------+---+      |
        |        |        |            |  +-------+
        |        |        |            |
        |        |        |            |
        |        |        |            |
        |        |        |            |
        v        v        v            v
    
                 Hardware


Markup sux... |||||||  +---+  

Mono vs Micro
^^^^^^^^^^^^^

The linux kernel is monolithic, and runs as a single binary in the same privileged kernel memory space. This allows different parts of the kernel to call other parts directly via their function names, and communicate that way.  This is in contrast to a microkernel, which runs different kernel features in different "services", which use some IPC protocol to communicate, and which should only run in user space unless they absolutely need priviledged execution. In practice, todays microkernels (OS X and Windows) all have services which run in kernel space in order to avoid the cost of context switching and latencies involved with IPC.

The downside of running everything as a single binary (monolithic) might be that a single misbehaving driver might tie up execution and bring down the whole OS, or a slow running system call may affect performance of the whole system. This is why the linux kernel was designed to be **preemptive**. The linux kernel can preempt (ie: the scheduler can forcibly perform a **context switch** on behalf of a runnable and higher priority process) a task even as it executes in the kernel, rather than co-operatively waiting for the task (driver or system call / other function) to complete and return control of the processor to the scheduler.

Misc
^^^^

- When a user space application attempts an illegal memory access, the kernel can trap the error, send the SIGSEGV signal, and kill the process. This is called memory protection. If the kernel attempts an illegal memory access, there's nobody to look after the kernel itself, so it generates an *oops* and panics.
- **paging** is a memory management scheme by which a computer stores and retrieves data from *secondary storage* for use in main memory. In this scheme, the OS retrieves data from secondary storage in same-size blocks called **pages**. This is not necessarily just paging to and from swap space, rather physical files on disk which a program is not using may remain there, while requested files may be paged into memory when they are accessed (ie: when a *page fault* is generated by the processor whilst performing some task for a process)
  - When a program tries to reference a page not currently present in RAM, the processor treats this invalid memory reference as a page fault and transfers control form the program to the OS
  - The OS must then determine the location of data on disk, obtain an empty page frame in RAM to use as a container for the data, load the requested data into the page frame, update the page table to refer to the new page frame, and then return control to the program, transparently retrying the instruction that caused the page fault in the first place.


Process Management
------------------

The Process
^^^^^^^^^^^

Processes:
- Are programs (object code stored on some media) in the midst of execution
- Contain a set of resources including:
  - open files and pending signals
  - internal kernel data
  - processor state
  - a memory address space with one or more memory mappings
  - one or more *threads of execution*
  - a *data section* containing global variables

Threads of execution are objects of activity within the process. Each thread includes:
- A unique program counter, process stack, and set of processor registers

The kernel schedules individual threads, not processes. To the linux kernel, a thread is just a special kind of process.

In linux, processes provide two virtualizations: a virtualized processor, and virtual memory. The virtual processor gives the process the illusion that it alone monopolizes the system, despite possibly sharing the processor with hundreds of other processes. Virtual memory lets the process allocate and manage memory as if it alone owned all the memory in the system.

Note that threads share the virtual memory abstraction, whereas each thread receives its own virtualized processor.

A program itself is not a process. A process is an *active* program and related resources. It's fully possible for two or more processes to exist which are executing the same program. These processes can share various resources, such as open files or an address space.

**Another name for a process is a task***. The linux kernel internally refers to processes as tasks.

Process Descriptor & Task Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- The kernel stores the list of processes in a circular doubly linked list called the *task list*
- Each element in the task list is a *process descriptor* of the type **struct task_struct**, which contains all the information about a specific process
- The task_struct contains a processes' open files, address space, pending signals, process state, *parent*, *children(s)*, and much more
- Outside of the kernel, processes are identified by a unique *process identification* value or *PID*. Typical max is 32k (short int) due to legacy support, but can be raised via /proc/sys/kernel/pid_max
- Inside the kernel, tasks are typically referenced directly by a pointer to their task_struct structure. Nearly any kernel function that deals with processes works directly with struct task_struct.

Process State
^^^^^^^^^^^^^

The *state* field of the process descriptor describes the current condition of the process. Each process on the system is in exactly one of five different states, represented by five flags:

- **TASK_RUNNING** : The process is runnable - either currently running, or on a run-queue waiting to run
- **TASK_INTERRUPTIBLE** : The process is sleeping (that is, it is **blocked**), waiting for some condition to exist. When this condition exists, the kernel sets the process's state to TASK_RUNNING. The process also awakes prematurely and becomes runnable if it receives a signal
- **TASK_UNINTERRUPTIBLE** : Identical to INTERRUPTIBLE except that it does *not* wake up and become runnable if it receives a signal. Thi sis used in situations where the process must wait without interruption, or when the event is expected to occur quite quickly. Because the task does not respond to signals in this state, it is less often used
- **__TASK_TRACED** : The process is being *traced* by another process, such as a debugger, via *ptrace*
- **__TASK_STOPPED** : Process execution has stopped; the task is not running nor is it eligible to run. This occurs if the task receives the SIGSTOP, SIGTSTP, SIGTTIN, or SIGTTOU signal or if it receives *any* signal while it is being debugged

Process Context
^^^^^^^^^^^^^^^
Normal program execution occurs in *user-space*. Whyen a rpogram executes in a system call or triggers an exception, it enters *kernel-space*. At this point, the kernel is said to be "executing on behalf of the process" and is in **process context**.

Upon exiting the kernel, the process resumes execution in user-space, unless a higher priority process has become runnable in the interim, in which case the schedule is invoked to select the higher priority process.

**All** access to the kernel is through system calls an exception handlers. A process can begin executing in kernel space only through one of these interfaces.


Process Creation
----------------

General
^^^^^^^
The child process created by fork() is an exact copy of the current (parent) task. It differs from the parent only in its PID (which is unique), its PPID (paren'ts PID, which is set to the original process), and certain resources and statistics, such as pending signals, which are not inherited.

Copy-on-write is used such that the parent and child both point to the same resources. Shared read-only. If writes occur, a duplicate of the affected data is made and each process receives a unique copy. This occurs on a per-page basis.

Each process has its own page tables. The parent page tables are copied to the child's upon fork. As such, the only overhead incurred by fork is this copying of page table and the creation of a unique process descriptor (task_struct) for the child.

Forking
^^^^^^^
The glibc libraries fork(), vfork(), and __clone() all call the clone() system call using various flags which specify which resources, if any, the parent and child process should share.

The clone() system call in turn calls do_fork(). This then calls copy_process, which does most of the interesting work.

- fork()/vfork() calls sys call clone()
- clone() -> do_fork() -> copy_process()
- copy_process -> dup_task_struct() which creates new kernel stack, thread_info, and task_struct
  - child and parent descriptors identical at this point
- copy_process -> stats/misc cleared from child proc descriptor. Child state set to TASK_UNINTERRUPTIBLE to prevent scheduling incomplete task
- copy_process -> copy_flags() to update the *flags* member of task_struct. PF_SUPERPRIV cleared. *PF_FORKNOEXEC set, denoting that it is a process that has not called exec()*
- copy_process -> alloc_pid(), assigned to pid slot of child task_struct
- copy_process -> depending on flags passed to clone(), duplicates or shares open files, filesystem info, signal handlers, process address space, and namespace. *These resources are typically shared between threads in a given process*, otherwise they are *unique and thus copied*.
- copy_process -> return pointer to new child. do_fork() picks up, wakes up child and child gets ran
- child gets ran **first** before the parent, to avoid COW overhead, as child typically immediately calls exec() whereas parent may continue writing into its address space immediately

**vfork()**: Has the same effect as fork(), except that the page *table* entries of the parent process are not copied. Instead, the child executes as the sole thread in the parent's address space, and the *parent is blocked until the child calls exec()* or exits. Messy! This was a legacy improvement back when fork() didn't do COW on pages. These days it is not useful unless for some reason making a copy of the parent process page tables during regular clone() has a big overhead. In the future, copy-on-write may be implemented for page tables as well, making vfork() fully deprecated.

Threads in Linux
^^^^^^^^^^^^^^^^
To the linux kernel, there is no concept of a thread. All threads are implemented as standard processes.

Each process gets its own unique task_struct. The kernel treats each as normal. The difference is that each thread may point to the same shared resources, such as address space, as other threads.

Threads are created the same as normal tasks, with the exception that clone() is called with flags corresponding tot he specific resources being shared:

  clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND, 0);

The above code will create a child process which shares its address space, filesystem resources, file descriptors, and its signal handlers with its parent.

A normal fork() call to clone would simply be:

  clone(SIGCHLD, 0);

Kernel Threads
^^^^^^^^^^^^^^
The kernel has threads too! It is often useful for the kernel to perform some operations in the background. Kernel threads are standard processes which exist  solely in kernel-space. The significant difference between kernel threads and normal processes is that kernel threads do not have an address space (their mm pointer, which points at their address space, is NULL). They do not context switch to user space. They are, however, schedulable and preemptable.

Most notably, the kernel delegates the *flush* tasks and the *ksoftirq* task to kernel threads. All the items in [brackets] that you see in ps -ef are kernel threads.

A kernel thread may only be created by another kernel thread. The kernel handles this automatically by forking all new kernel threads off of the *kthreadd* process. A kernel process can be created and made runnable by calling kthread_create() followed by wake_up_process(), or by calling kthread_run() which does both. It will continue to exist until it calls do_exit() or another part of the kernel calls kthread_stop(), passing in the address of the task_struct structure returned by kthread_create().

Process Termination
^^^^^^^^^^^^^^^^^^^
Generally a process terminates itself, when it calls the exit() system call. The exit() call may also be implied, for example if the main() function of the process ends and then C compiler places a call to exit() afterwards automatically.

An involuntary termination can happen when the process receives a signal or exception it cannot handle or ignore. Regardless of how a process terminates, teh bulk of the work is handled by do_exit().

- PF_EXITING flag in the flags member of the task_struct is set
- del_timer_sync() to remove any kernel timers, acct_update_integrals() to write out remaining proc accounting if BSD process accounting is enabled
- exit_mm() to release teh mm_struct help by the process. If no other proc sharing that mem space, kernel destroys it
- exit_sem() : if the proc is queued waiting for a semaphore, it is dequeued
- exit_files() , exit_fs() to decrement the usage count of objects related to file descriptors and filesystem data
- sets tasks exit code, stores in exit_code member of task_struct. Stored for optional retrieval by the parent
- exit_notify() called to send signals to the task's parent, reparents any of the task's children to another thread in their thread group or the init process, and sets the task's exit state, stored in *exit_state in the task_struct* to *EXIT_ZOMBIE*
- do_exit() then calls schedule() to switch to a new process. Since the process is no longer schedulable, do_exit() never returns

At this point, all objects associated with the task are freed, the task is not runnable (and no longer has address space to run), and is in the EXIT_ZOMBIE exit state. The only memory it occupies is its kernel stack - the thread_info and task_struct structures. The task exists solely to provide information to its parent.

The parent will typically call wait() right after the fork(), and may choose to wait for wait() to return with the PID of the exited child. Additionally, a pointer is returned which holds the exit code of the terminated child.

release_task() is then called (by whom? triggered by wait()?) which cleans up the exited PID from task lists, releases any remaining resources, and frees pages containing the process's kernel stack and thread_info structure, and deallocate the slab cache containing the task_struct.

ptrace
^^^^^^
The kernel has a feature where tasks can be *ptraced*. What this does is allow a debugger to temporarily **re-parent** a task to itself. A separate list is kept of the original parents of ptraced tasks such that when the debugger exits, the task can have its PPID set back to the original value.

Process Scheduling
------------------
The linux kernel is a multitasking operating system which uses *preemptive multitasking* (in contrast with cooperative multitasking). The scheduler decides when a process is to cease running and a new process is to begin running.

The act of involuntarily suspending a running task is called *preemption*. The time that a process runs before it is preempted is usually predetermined, and is called the *timeslice* of the process. The timeslice, in effect, gives each runnable process a *slice* of the processor's time.

Each process runs for a "timeslice" that is proportional to its weight divided by the weight of all other runnable tasks.

<input more about CFQ and proportion of the processor - page 46>

Sleeping and Waking Up
^^^^^^^^^^^^^^^^^^^^^^
Sleeping (blocked) tasks are in a special nonrunnable state. This is important because without this special state, the scheduler would select tasks that did not want to run, or worse, sleeping would have to be implemented as a busy loop.

A task always sleeps because it is waiting for some event. The event can be a specified amount of time, more data from a file I/O, or another hardware event. A task can also involuntarily go to sleep when it tries to obtain a contended semaphore.

Processes put themselves on a wake queue and mark themselves not runnable. When the event associated with the wait queue occurs, the processes on the queue are awakened.

# __add_wait_queue() adds task to a wait queue, sets the task's state to TASK_INTERRUPTIBLE, can calls schedule(). schedule() calls deactivate_task() which removes the task from the runqueue
# (task not runnable) : even the task is waiting for occurs, and try_to_wake_up() sets the task to TASK_RUNNING, calls activate_task() to add the task to a runqueue, and calls schedule(). __remove_wait_queue() removes the task from the wait queue
# (task not runnable) OPTION 2 : task receives a signal. task state set to TASK_RUNNING and task executes signal handler
# task now running


Preemption and Context Switching
--------------------------------
Context switching, the switching from one runnable task to another, is handled by the *context_switch()* function. It is called by *schedule()* when a new process has been selected to run. It does two basic jobs:

- Calls *switch_mm()* to switch the virtual memory mapping from the previous process's to that of the new process
- Calls *switch_to()* to switch the processor state from the previous process's to teh current's. This involves saving and restoring stack information and the processor registers and any other architecture-specific state that must be managed and restored on a per-process basis

pg.62
The kernel needs to know when to actually call schedule(). This is done by setting the need_resched flag of a given process (stored in thread_info). The kernel, upon returning to user space or an interrupt, will check for the need_resched flag of each process. If it is set, the kernel invokes the scheduler before continuing.

User Preemption
^^^^^^^^^^^^^^^
User preemption occurs when the kernel is about to return to user space, need_resched is set, and therefore, the scheduler is invoked. If the kernel is returning to user space, it knows that it is in a safe quiescent state and as such it is safe to pick a new task to execute (or continue executing current task).

User preemption can occur:

- When returning to user-space from a system call
- When returning to user-space from an interrupt handler

Kernel Preemption
^^^^^^^^^^^^^^^^^
The kernel can preempt a task running in the kernel so long as it does not hold a lock. Because the kernel is SMP-safe, if a lock is not held, teh current code is reentrant and capable of being preempted. A preempt_count counter exists in each process's thread_info. This counter begins at zero, and is incremented for each lock that is acquired and decrements for each lock that is released. When the counter is zero, the kernel is preemptible.

Upon return from interrupt, if returning to kernel-space, the kernel checks the values of need_resched and preempt_count. If need_resched is set and preempt_count is zero, then a more important task is runnable, and it is safe to preempt (run schedule()). Otherwise, it is not safe to preempt and the interrupt returns as usual to the currently executing task.

Additionally, when all locks that the current task is holding are released and preempt_count returns to zero, the unlock code checks whether need_resched is set. If so, the scheduler is invoked.

Kernel preemption can occur:

- When an interrupt handler exits, before returning to kernel-space
- When kernel code becomes preemptible again
- If a task in the kernel explicitly calls schedule()
- If a task in the kernel blocks(sleeps) (which results in a call to schedule())

CPU Affinity
^^^^^^^^^^^^
The linux scheduler provides a soft attempt to keep processes rescheduled to the same processor. It also provides the option of hard affinity, where a process must be scheduled on a certain processor. This is done by setting a bitmask in *cpus_allowed* inside each task's task_struct to whichever processor(s) you'd like.

You can set this via the sched_affinity() system call. sched_getaffinity() will get the current settings.


System Calls
------------

System calls provide a layer between hardware and user-space processes, and serve three main use cases.

First, it provides an abstracted hardware interface for user-space. When readin gor writing from a file, for example, applications are not concerned with the type of disk, media, or even the type of filesystem on whihc the file resides.

Second, system calls ensure system security and stability. With the kernel acting as a middle-man between system resources and user-space, the kernel can arbitrate access based on permissions, users, whether an application is correctly using hardware, prevent processes from stealing other processes resources, and other features.

Third, a single common layer between user-space and the rest of the system allows for the virtualized system provided to processes. If applications were free to access system resources without the kernel's knowledge, it would be nearly impossible to implement multitasking and virtual memory (and with security and stability).

In linux, system calls are the only means user-space has of interfacing with the kernel; they are the only legal entry point into the kernel other than exceptions or traps. Indeed, other interfaces, such as device files or /proc, *are ultimately accessed via system calls*. 

    application calls printf() ---> printf() in the C library ---> write() system call

In linux, each system call is assigned a *syscall number*. This is a unique number that is used to reference a specific system call. When a user-space process executes a system call, the syscall number identifies which syscall was executed - the process does not refer to the syscall by name (except in the source code itself). This number is important; when assigned, it cannot change, or compiled applications will break.


System Call Handler
^^^^^^^^^^^^^^^^^^^

A user-space application cannot execute kernel code directly. They cannot simply make a function call to a method existing in kernel-space, because the kernel exists in a protected memory space. Instead, user-space applications must somehow signal to the kernel that they want to execute a system call and have hte system switch to kernel mode, where the system call can be executed in kernel-space by the kernel on behalf of the application.

To do this, a process will throw a software interrupt, and user-space will stick whatever system call number is wanted into the *eax* register and then cause a trap into the kernel. The system call handler will then read the value from eax. This number is validated against NR_syscalls, and if the number is less than NR_syscalls, the specified system call is invoked.

In addition to system call number, most syscalls need one or more parameters passed to them. This is typically done, as is the case for the syscall number, by user-space storing these parameters in registers (ebx, ecx, edx, esi, edi). The return value is sent to user-space also via register (typically in eax).


Kernel Data Structures
----------------------
Start pg 86.


