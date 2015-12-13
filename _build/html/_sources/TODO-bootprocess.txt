~~Boot~~
-Bootstrap loader on MB is loaded. It looks for MBR in first 512bytes. 
-Bootstrap loader starts stage1 bootloader, first sector of disc
-/boot partition sector location is in mbr. stage1 uses the location to launch stage 1.5(if disk is 2TB+) or 2 bootloader
-stage2 (eg:grub) loads the decompressed kernel image and initrd into memory and then invokes the kernel process
-Kernel initializes some hardware and sets up initrd in memory
-init script in initrd sets up /proc, /sys, /dev and other essentials, as well as provides some basic needed tools like insmod
-some basic modules are loaded (such as scsi & sata drivers, ext3 module) and more hardware is initialized and added to /sys
-root is mounted read only
-Kernel runs init
-SYSVINIT....kernel runs rc.sysinit
-rc.sysinit makes sure modprobe (an intelligent wrapper for insmod) and starts udev
-udev and modprobe combine forces to read available modules, stuff in /sys, and use that info to create /dev nodes
-rc.sysinit then goes on to set kernel params, other crap, and then remounts root to rw using info in /proc/mounts. Then mtab is generated, then swap is initialized.
-after init is done with rc.sysinit, it calls inittab
-inittab loads your various services based on your runlevel
-inittab then makes some virtual tty's by running mingetty for each runlevel and asks you for a username
-mingetty passes your username to login. login verifies, then passes to (probably)bash
-bash starts, bootup done.


TODO: UEFI notes
