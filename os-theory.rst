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
- The task_struct contains a processes' open files, address space, pending signals, process state, and much more
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

