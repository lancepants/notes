Boot Process
============

Legacy Boot
-----------
- Bootstrap loader on MB is loaded. It looks for MBR in first 512bytes. 
- Bootstrap loader starts stage1 bootloader, first sector of disc
- /boot partition sector location is in mbr. stage1 uses the location to launch stage 1.5(if disk is 2TB+) or 2 bootloader
- stage2 (eg:grub) loads the decompressed kernel image and initrd into memory and then invokes the kernel process
- Kernel initializes some hardware and sets up initrd in memory
- init script in initrd sets up /proc, /sys, /dev and other essentials, as well as provides some basic needed tools like insmod
- some basic modules are loaded (such as scsi & sata drivers, ext3 module) and more hardware is initialized and added to /sys
- root is mounted read only
- Kernel runs init
- SYSVINIT....kernel runs rc.sysinit
- rc.sysinit makes sure modprobe (an intelligent wrapper for insmod) and starts udev
- udev and modprobe combine forces to read available modules, stuff in /sys, and use that info to create /dev nodes
- rc.sysinit then goes on to set kernel params, other crap, and then remounts root to rw using info in /proc/mounts. Then mtab is generated, then swap is initialized.
- after init is done with rc.sysinit, it calls inittab
- inittab loads your various services based on your runlevel
- inittab then makes some virtual tty's by running mingetty for each runlevel and asks you for a username
- mingetty passes your username to login. login verifies, then passes to (probably)bash
- bash starts, bootup done.


UEFI
----
In essence, UEFI does away with stage 1 and 1.5 bootloaders.

https://www.happyassassin.net/2014/01/25/uefi-boot-how-does-that-actually-work-then/

tl;dr
^^^^^
- UEFI is firmware. Its config is in NVRAM on your motherboard. It most resembles a stage2 bootloader. Think grub/lilo+menu.cfg built into firmware, with its entries pointed to other "stage 2" bootloaders on various disks/devices.
- In the case of booting a live disk or install media from a storage device, UEFI reads GPT formatted disks. It gets disk GUID and partition GUID, as well as which partitions are marked "0" (system, aka efi FAT system partition) from GPT info at the start or end of the GPT-labelled storage device. It uses this info to look for bootloaders.efi to load.
- OS's run efibootmgr when installing. They generate their own entry in UEFI by taking info from GPT and running efibootmgr -c ...stuff, which generates an entry in your EUFI firmware's config like (diskGUID,partitionGUID)(/efi/grub.efi).
- Use efibootmgr to read/write configs. You can determine what boots first, boot once, blah blah "man efibootmgr"
- UEFI can also detect non storage devices to boot from, such as network cards. It scans ACPI and other paths to find valid resources, based on the EFI_DEVICE_PATH_PROTOCOL section of its spec.
- OS's are now expected to manage themselves and their own bootloaders only, stay out of everyone else's business. In practice, this is not really the case, as UEFI spec is not strict enough.
- Your UEFI firmware can ship with a set of signatures. It can refuse to run any EFI executable which is not signed with one of those signatures. This is what Secure Boot is.

Forward
^^^^^^^

UEFI and BIOS are two types of firmware. Saying a computer has a UEFI BIOS is nonsensical.
As we know, BIOS will look at a disks' MBR for a magic bit and then load the stage1 bootloader. It has no idea what a partition is, or what an OS is - it doesn't care. Stage1 bootloader loads stage2 (or possibly stage1.5), stage2 has the OS list and which partition to load them from, blah blah, normal BIOS boot procedure. UEFI is different...it removes some of the steps in this awkward chain-loading process, and moves a lot of "stage 2" bootloader type functionality into the UEFI firmware itself. Read on.

When you use UEFI "legacy/compatability" boot mode, all UEFI is doing is loading the stage1 bootloader off of a drive's MBR. It's kicking off the old-style BIOS bootloading.

This document describes native UEFI bootloading. It also assumes the use of disks with GPT partition table and EFI FAT32 EFI system partitions (EFI FAT32 ESPs). Crapintosh's may not conform to this assumption, but 99% of other stuff will.

The GPT (GUID partition table) is very much tied into the UEFI spec, and in fact, is necessary to understand in order to know how UEFI figures out a lot of its information. This document includes a foray into GPT structure.

UEFI Can:
-Read a partition table (GPT)
-Access files in some specific filesystems (FAT32, others)
-Execute code in a particular format
-Boot multiple *targets* - not just disks

##
How does UEFI find various possible boot targets? How do I configure boot targets?
##
The UEFI spec defines something called the UEFI boot manager. In Linux, there's a tool called
  efibootmgr
which is used to manipulate the config of the UEFI boot manager. The UEFI Boot Manager is a firmware policy engine that can be configured by modifying global NVRAM variables. The boot manager will attempt to load UEFI drivers and UEFI applications (including UEFI OS bootloaders) in an order defined by these NVRAM variables. In a sense the UEFI Boot Manager is kind of like a stage2 bootloader (ie: grub/lilo menu.cfg). You can add and remove stuff from it, and change the order in which stuff boots. The values though, are saved to NVRAM on your motherboard rather than to an MBR or something on an attached device.

Take a look at your current UEFI settings: 
  efibootmgr -v
    BootCurrent: 0000
    Timeout: 5 seconds
    BootOrder: 0000,0080
    Boot0000* Fedora    HD(4,797c000,64000,60ffa404-df04-48dc-825e-13ae506e0db5)File(\EFI\fedora\shim.efi)
    Boot0004* Hard Drive    BIOS(2,0,00)P0: ST1500DM003-9YN16G
    Boot0080* Mac OS X  HD(1,28,64000,f9a29f55-388b-46e5-b5ba-3afa21d1fa57)File(\EFI\refind\refind_x64.efi)
    Boot0081* Recovery OS   ACPI(a0341d0,0)PCI(1c,5)PCI(0,0)SATA(0,0,0)HD(3,7845e20,135f20,88bc09aa-aafb-4874-be13-ec21dabd7070)File(\com.apple.recovery.boot\boot.efi)
    Boot0082*   ACPI(a0341d0,0)PCI(1c,5)PCI(0,0)SATA(0,0,0)HD(3,7845e20,135f20,88bc09aa-aafb-4874-be13-ec21dabd7070)
    BootFFFF*   ACPI(a0341d0,0)PCI(1c,5)PCI(0,0)SATA(0,0,0)HD(3,1d250438,135f20,88bc09aa-aafb-4874-be13-ec21dabd7070)File(\System\Library\CoreServices\boot.efi)


It is encouraged to man efibootmgr. It has an examples section which is quite useful. eg:
  efibootmgr [-n | --bootnext] 0080  #Boot into 0080 next boot instead of default (just once)
    BootNext: 0080
    BootCurrent: 0000
    ...

When you installed your OS, it likely has already populated your UEFI with its efi bootloader information. For other entries, UEFI is finding boot targets itself.

So how does EFI find these boot targets? Well...crack open the EFI_DEVICE_PATH_PROTOCOL section of the spec if you really want to get into how UEFI defines what a possible boot target could be. This is a generic protocol that’s used for other things than booting – it’s UEFI’s Official Way Of Identifying Devices For All Purposes, used for boot manager entries but also for all sorts of other purposes. Not every possible EFI device path makes sense as a UEFI boot manager entry, for obvious reasons (you’re probably not going to get too far trying to boot from your video adapter). But you can certainly have an entry that points to, say, a PXE server. The spec has lots of bits defining valid non-disk boot targets that can be added to the UEFI boot manager configuration.

In the case of finding bootable attached storage, UEFI needs that disk to either have an MBR(legacy) or be formatted with a GPT. From a disks' GPT, UEFI can generate a target path and look for efi bootloaders. Read on.

##
A quick foray into GPT
##
GPT allocates 64 bits for logical block addresses (LBA = a pointer to a location on disk). So with 64 bits of space, we can address up to 2^64 locations on disk. Now this is where sectors come in. Each of these LBA's points to a sector on disk. A typical sector size is 512 bytes, so given this assumption we are able to address 2^64 locations of 512 byte sectors. 2^64*512b=9.4ZB

HDD manufacturers are starting to transition to 4096byte sectors. Unfortunately, many of these drives are often still presenting 512byte sectors to the OS. This can cause misaligned writes, causing two disk IO operations each time a single misaligned 4KB write operation occurs. Such a misalignment occurs by default if the first partition is placed immediately after the GPT, as the first usable block after (default) GPT is LBA 34, whereas the next 4 KB boundary begins with LBA 40. Keep this in mind when choosing hdds and when configuring sector sizes for your LUNs in your RAID config (you want your presented sector size to match your actual disk sector size).

LBA 0 : At the start of your storage device, the first logical block address, exists a "protective MBR" which allows a BIOS-based computer to recognize the disk and boot from it. Note that the bootloader (ie: grub/other) has to support GPT, and so does your OS
LBA 1 : GPT header. Has: your disk GUID, number and size of partition entries that make up partition table (minimum 16KB reserved for partition table array, which translates to 128 partition entries @ 128bytes each), size and location of secondary GPT header table (the backup GPT at the end of the disk), and a checksum! (this means manually modifying GPT with a hex editor makes the checksum invalid, resulting in other firmwares thinking your GPT is corrupt and possibly triggering automated recovery from your secondary GPT).
LBA 2 : First 4 entries of your partition table, or "Partition Entry Array". Values: partition GUID, first LBA, last LBA, attributes (0-system partition, 1-EFI ignore me, 2-Legacy BIOS bootable ..), etc. 128bytes total per entry.
LBA 3 : Partition Entry Array entries 5 through 128
LBA 34 : First usable sector. Why LBA 34? On a disk having 512-byte sectors, a partition entry array size of 16,384 bytes and the minimum size of 128 bytes for each partition entry, LBA 34 is the first usable sector on the disk.
LBA -33 : Backup partition table entries (first four)
LBA -32 to -2 : Backup partition table entries (remaining)
LBA -1 : Secondary GPT header


Back to UEFI
^^^^^^^^^^^^
When talking about booting from storage devices where there is not already a target configured in UEFI (live images, OS install media)
So from the above, we find that UEFI reads an attached storage device's GPT and looks through its Partition Entry Array for partitions with attribute "0" (efi system partition). From the GPT it also gets your disk GUID and your partition GUIDs. So you have the disk and the partition path, but what .efi bootloader should be ran if booting from that target? Perhaps you are trying to boot from a live image. In this instance, UEFI has default locations that it looks in. Namely, for x86_64, /EFI/BOOT/BOOTx64.EFI  (where x64 is actually a "machine type short-name"). It could also look for BOOTIA32.EFI, BOOTARM.EFI, etc etc..

How does an OS configure UEFI?
When you install an OS that has native UEFI support, at some point in the setup process it will look for an existing EFI system partition (and create one if it doesn't exist), drop its EFI bootloader onto it, then call efibootmgr -c {some options here}. By default just running "efibootmgr -c" assumes that /boot/efi is your EFI system partition, and is mounted at /dev/sda1. It'll drop in elilo.efi and make a new entry called "Linux" at the top of the boot order.
You can have as many EFI system partitions as you want wherever you want...remember the UEFI entries (which exist in NVRAM) reference both a disk GUID and a partition GUID.


A quick recap
^^^^^^^^^^^^^
* Your UEFI firmware contains something very like what you think of as a boot menu.
* You can query its configuration with efibootmgr -v, from any UEFI-native boot of a Linux OS, and also change its configuration with efibootmgr (see the man page for details).
* This ‘boot menu’ can contain entries that say ‘boot this disk in BIOS compatibility mode’, ‘boot this disk in UEFI native mode via the fallback path’ (which will use the ‘look for BOOT(something).EFI’ method described above), or ‘boot the specific EFI format executable at this specific location (almost always on an EFI system partition)’.
* The nice, clean design that the UEFI spec is trying to imply is that all operating systems should install a bootloader of their own to an EFI system partition, add entries to this ‘boot menu’ that point to themselves, and butt out from trying to take control of booting anything else.
* Your firmware UI has free rein to represent this mechanism to you in whatever way it wants, and it may do this well, or it may do this poorly.

An important caveat
^^^^^^^^^^^^^^^^^^^
If you boot the installation medium in ‘UEFI native’ mode, it will do a UEFI native install of the operating system: it will try to write an EFI-format bootloader to an EFI system partition, and attempt to add an entry to the UEFI boot manager ‘boot menu’ which loads that bootloader.
If you boot the installation medium in ‘BIOS compatibility’ mode, it will do a BIOS compatible install of the operating system: it will try to write an MBR-type bootloader to the magic MBR space on a disk.

This is an important distinction! Be aware of which mode you are using when you do your installs. If you want UEFI, use it all the way through. If you're not sure which mode you've booted into in your installer, ctrl-alt-f2 and run efibootmgr -v. It shouldn't error out. If it does, complaining about sysfs/procfs entries for EFI variables not there blah blah then you're in legacy boot mode.
Remember when creating livecd iso-to-disk's that your media needs to comply with UEFI if you want it to boot as UEFI. This means it’s got to have a GPT partition table, and an EFI system partition with a bootloader in the correct ‘fallback’ path – \EFI\BOOT\BOOTx64.EFI (or the other names for the other platforms). Tools like livecd-iso-to-disk will do this for you if you pass --efi to it.

You've also got to worry about booting an installer in UEFI mode, and (without formatting) installing to a disk that is already MBR. Don't do this, you're asking for failure. parted /dev/sdx will show you your Partition Table type.

Secure Boot in a nutshell
^^^^^^^^^^^^^^^^^^^^^^^^^
Your UEFI firmware can ship with a set of signatures. It can refuse to run any EFI executable which is not signed with one of those signatures. That's basically it! So why are people so pissed off about it? Because assholes (microsoft, shipping windows 8 or newer pre-installed) can ship their firmware with secure boot enabled by default, and even though UEFI spec *requires* that a user must be able to disable secure boot, microsoft doesn't care! Microsoft x86 spec says "Allow a physically present person to disable Secure Boot", while their ARM computers shipped from microsoft spec must NOT allow secure boot to be turned off! Now you end up working through a bunch of BS (or not being able) to install another OS because your fedora install doesn't have a signed bootloader.efi.

And it's not just microsoft (as mentioned above, MS actually explicitly protect your right to determine what you can boot on your system *on x86 systems*). All iDevices and some Android devices implement secure boot - that's how they enforce a locked bootloader. This is why people have to come up with exploits in order to patch the system firmware to disable secure boot and allow other builds to be installed on the device. Don't like it? Don't buy it!


Crapintosh
^^^^^^^^^^
Apple ships at least some Macs with their bootloaders in an HFS+ partition. The spec says a UEFI-compliant firmware must support UEFI FAT partitions with the specific GPT partition type that identifies them as an “EFI system partition”, but it doesn’t say the firmware can’t also recognize some other filesystem type and load a bootloader from that. Now everyon else has to deal with it. Additionally, Apple also goes quite a long way beyond the spec in its boot process design, and if you want your alternative OS to show up on its graphical boot menu with a nice icon and things, you have to do more than what the UEFI spec would suggest. 

PXE Booting
^^^^^^^^^^^
!! Add me !!

