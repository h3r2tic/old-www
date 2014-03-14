import os
import sys
import traceback
import ssh
import time
import pickle
import threading

# setup logging
ssh.util.log_to_file('incremental_update_sftp.log')
os.chdir( 'output' )

def humanize_bytes(bytes, precision=1):
    abbrevs = (
        (1<<50L, 'PB'),
        (1<<40L, 'TB'),
        (1<<30L, 'GB'),
        (1<<20L, 'MB'),
        (1<<10L, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)

def get_local_dirs_files():
    local_dirs = set([])
    local_files = {}

    for root_, dirs, files in os.walk('.'):
        root = root_.replace('\\', '/')
        if root != '':
            local_dirs.add( root )
        for fname in files:
            fpath = ( fname if root == '' else root + '/' + fname )
            local_files[ fpath ] = os.stat( fpath ).st_mtime

    local_dirs = list(local_dirs)
    local_dirs.sort()

    return ( local_dirs, local_files )


class RemoteStorage(object):
    def __init__(self):
        self.t = None
        self.sftp = None
        self.file_list_index = '.incremental_updater_file_list'

    def __del__(self):
        self.t.close()

    def mkdir(self, dpath):
        try:
            self.sftp.mkdir( dpath, 0755 )
        except IOError:
            pass

    def get_file_list(self):
        try:
            return pickle.loads( self.sftp.open( self.file_list_index, 'rb' ).read() )
        except IOError:
            return ( {}, {} )

    def save_file_list(self, data):
        self.sftp.open( self.file_list_index, 'wb' ).write( pickle.dumps(data) )

    def connect(self):
        # get hostname
        username = 'h3gdpo'
        hostname = 'webhost.daily.co.uk'
        port = 22
        password = open('../password.txt', 'r').read()

        # get host key, if we know one
        hostkeytype = None
        hostkey = None
        keypath = None
        try:
            keypath = os.path.expanduser(r'C:\MinGW\msys\1.0\home\h3r3tic\.ssh\known_hosts')
            print keypath
            host_keys = ssh.util.load_host_keys(keypath)
        except IOError:
            try:
                # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                keypath = os.path.expanduser('/ssh/known_hosts')
                host_keys = ssh.util.load_host_keys(keypath)
            except IOError:
                print '*** Unable to open host keys file'
                host_keys = {}

        if host_keys.has_key(hostname):
            hostkeytype = host_keys[hostname].keys()[0]
            hostkey = host_keys[hostname][hostkeytype]
            print 'Using host key of type %s from %s' % (hostkeytype, keypath)


        self.t = ssh.Transport((hostname, port))
        self.t.connect(username=username, password=password, hostkey=hostkey)
        self.sftp = ssh.SFTPClient.from_transport(self.t)
        self.sftp.chdir('public_html')



remote = RemoteStorage()
remote.connect()

( remote_dirs, remote_files ) = remote.get_file_list()
( local_dirs, local_files ) = get_local_dirs_files()

for dpath in local_dirs:
    if dpath not in remote_dirs:
        remote.mkdir( dpath )

class UploadTask(object):
    def __init__(self, fpath, reason):
        self.fpath = fpath
        self.reason = reason
        self.size = os.stat( fpath ).st_size

upload_tasks = []

for fpath in local_files.keys():
    local_mtime = local_files[ fpath ]

    should_copy = False
    reason = ''

    if fpath not in remote_files:
        upload_tasks.append( UploadTask( fpath, 'missing ') )
    elif remote_files[ fpath ] < local_mtime:
        upload_tasks.append( UploadTask( fpath, 'obsolete') )

total_upload_size = sum( [ f.size for f in upload_tasks ] )

if total_upload_size > 0:
    def update_progress_bar( item, total_upload_done ):
        assert len(item.reason) <= 8
        progress_bar_width = 20
        file_name_width = 35
        max_line_width = 79

        i = progress_bar_width * total_upload_done / total_upload_size
        bar = '['
        bar += '*' * i
        bar += ' ' * ( progress_bar_width - i )
        bar += '] '
        bar += 'uploading %s "' % item.reason
        if len( item.fpath ) > file_name_width:
            bar += '...' + item.fpath[-file_name_width+3:]
        else:
            bar += item.fpath
        bar += '"'
        assert len( bar ) <= max_line_width, bar
        bar += ' ' * ( max_line_width - len( bar ) )
        sys.stdout.write( '\r' + bar )

    total_upload_done = 0

    print 'Total upload size:', humanize_bytes( total_upload_size )
    for t in upload_tasks:
        update_progress_bar( t, total_upload_done )
        def progress_func( cur, remaining ):
            update_progress_bar( t, total_upload_done + cur )
        remote.sftp.put( t.fpath, t.fpath, progress_func )
        total_upload_done += t.size


for fpath in local_files.keys():
    remote_files[fpath] = local_files[fpath]

#for d in local_dirs.keys():
#    remote_dirs[d] = local_dirs[d]

remote.save_file_list( ( remote_dirs, remote_files ) )
remote.t.close()


for thread in threading.enumerate():
    if thread is not threading.currentThread():
        thread.join()

print '\nUpload complete.'
