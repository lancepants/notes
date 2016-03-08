#!/usr/local/bin/python2.7

'''
This script takes a directory as input and then compresses and uploads its
contents (recursively) to an S3 bucket. This script overwrites the target files upon
duplicate key name. This script also uses multiple processes - please ensure all
child processes are terminated should you manually need to kill this program.

Requirement tracking:
  python27-boto
  -boto requires aws authentication. It will look in /etc/boto.cfg and ~/.boto.cfg.
  You can also explicitly define auth, but this script is assuming .boto.cfg exists.
'''
import math, os, sys, re, time
import fcntl
import argparse
import boto
import gzip
import cStringIO
from ctypes import c_int
from multiprocessing import Pool, Value, Lock
from multiprocessing.pool import ThreadPool
from cStringIO import StringIO
from boto.s3.key import Key
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument('-r', default='us-west-2', dest='region', help='S3 region. Default us-west-2 (Oregon)')
parser.add_argument('bucket', help='Name of bucket you want to operate in.')
parser.add_argument('sourcepath', help='Can be absolute or relative. Matching remote path is created. Note: This is recursive!')
args = parser.parse_args()

bucketname = args.bucket
sourcepath = args.sourcepath + '/'  # os module works with //
region = args.region

counter = Value(c_int)
counter_lock = Lock()

#boto.set_stream_logger('boto') #print debug logs

def getBucket(region, bucketname):
    s3 = boto.s3.connect_to_region(region)
    if s3.lookup(bucketname) is None:
        print "Can't find bucket %s!" % bucketname
        sys.exit(2)
    else:
        bucket = s3.get_bucket(bucketname)
    return bucket

def getFileList(sourcepath):
    filelist = []
    failed = []
    smfiles = []
    lfiles = []
    now = int(time.time())
    mtime_limit = 86400 # 24hrs

    def osError(oserror):
        print oserror
        failed.append(oserror.filename)
    for root, dirs, files in os.walk(sourcepath, onerror=osError):
        for f in files:
            fullpath = os.path.join(root, f)
            try:
                fmtime = int(os.stat(fullpath).st_mtime)
                if now - mtime_limit < fmtime:
                  filelist.append(fullpath)
            except:
                failed.append(fullpath)
                print "Failed to stat %s. File access permissions changed during this process execution" % fullpath
                pass
    for f in filelist:
        try:
            if os.stat(f).st_size < 100<<20: # If file size less than 100MB
                smfiles.append(f)
            else:
                lfiles.append(f)
        except:
            failed.append(f)
            print "Failed to stat %s. File access permissions changed during this process execution" % f
            pass
    if len(failed) != 0:
        print 'Warning: %d files were excluded due to file access errors.' % len(failed)
        #print failed
    return smfiles, lfiles

def fileUpload(f):
    conn = boto.s3.connect_to_region(region, is_secure=True)
    bucket = conn.get_bucket(bucketname)
    fobj = open(f, 'r')
    fgz = BytesIO()
    compressor = gzip.GzipFile(filename=f, mode='wb', fileobj=fgz)
    compressor.write(fobj.read())
    compressor.close()
    fgz.seek(0)
    s3obj = Key(bucket)
    if re.search('\.gz$|\.tgz$', f):
        s3obj.key = f
    else:
        s3obj.key = f + ".gz"
    s3obj.set_contents_from_file(fgz)
    #print "successfully uploaded %s" % s3obj.name
    increment()


def mpartFileUpload(f):
    conn = boto.s3.connect_to_region(region, is_secure=True)
    bucket = conn.get_bucket(bucketname)
    if re.search('\.gz$|\.tgz$', f):
        mpobj = bucket.initiate_multipart_upload(f)
    else:
        mpobj = bucket.initiate_multipart_upload(f + ".gz")
    stream = cStringIO.StringIO()
    compressor = gzip.GzipFile(fileobj=stream, mode='w')
    def uploadPart(partCount=[0]):
        partCount[0] += 1
        stream.seek(0)
        mpobj.upload_part_from_file(stream, partCount[0])
        stream.seek(0)
        stream.truncate()
    with file(f) as inputFile:
        """
        Read file 8K at a time, passing to gzip. Gzip
        fills the stringio stream object with compressed data.
        Once stream object size hits 50MB, it calls uploadPart
        """
        while True:
            chunk = inputFile.read(8192)
            if not chunk: #EOF
                compressor.close()
                uploadPart()
                mpobj.complete_upload()
                break
            compressor.write(chunk)
            if stream.tell() > 100<<20: # "<<" does a bit shift. eg makes 200 = 200MB
                uploadPart()
    #print 'successfully uploaded %s' % mpobj.key_name
    increment()

def increment():
    with counter_lock:
        counter.value += 1
    print "uploads complete.                   \r", counter.value,
    sys.stdout.flush()

def lockFile(lockfile):
    fd = os.open(lockfile, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True

if __name__ == '__main__':
    #This lockfile implementation fails in the case of the master process dieing while
    #child processes continue their attempt to finish their last 'large' file. An
    #improvement on this implementation may require further external dependencies, and
    #as such is omitted for now.
    if not lockFile("/tmp/.s3thinger.lock"):
        print "Could not acquire lockfile. Please ensure no other instances of this script are running"
        sys.exit(2)

    smfiles, lfiles = getFileList(sourcepath)
    totalFileCount = len(smfiles) + len(lfiles)
    print "%d files scheduled for upload." % totalFileCount
    #pool = Pool(initializer = counterInit, initargs = (counter, ))
    pool = Pool()
    pool.map_async(mpartFileUpload, lfiles)
    threadpool = ThreadPool(processes=32)
    threadpool.map_async(fileUpload, smfiles)
    pool.close()
    pool.join()
    threadpool.close()
    threadpool.join()

