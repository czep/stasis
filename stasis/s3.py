import pathlib
import re
import datetime
from dateutil.tz import tzutc
import fnmatch
import mimetypes
import os
import pprint
import hashlib
import string
import gzip
import shutil

import boto3

# fixed timestamp to insert into gzip header
# required to ensure that subsequent gzips of the same
# file will have the same hash
# see: https://stackoverflow.com/questions/264224/
MAGICTIME = 999999999

def keysort(d):
    return {k: d[k] for k in sorted(d)}

def to_uri(path, basepath):
    return re.sub(basepath, '', str(path.resolve()))

def to_date(ts):
    return datetime.datetime.fromtimestamp(ts, tzutc())

def pattern_match(filename, pattern_list):
    found = False
    for pattern in pattern_list:
        if fnmatch.fnmatch(filename, pattern):
            found = True
            break
    return found

def get_object_dict(filelist):
    object_list = []
    for f in filelist:
        object_list.append({'Key': f})
    d = {'Objects': object_list}
    return d

def md5(file):
    md5hash = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5hash.update(chunk)
    return md5hash.hexdigest()

def files_differ(local, remote):
    if local['ETag'] != remote['ETag']:
        return True
    else:
        return False

def compress_copy(filename, compresslevel):
    zipfilename = filename.with_name(str(filename.name) + ".upload")
    with open(filename, 'rb') as f_in:
        with gzip.GzipFile(zipfilename, 'wb', compresslevel=compresslevel, mtime=MAGICTIME) as f_out:
            shutil.copyfileobj(f_in, f_out)
    return zipfilename


class S3():
    def __init__(self, args, config):
        self.s3_bucket = config['S3_BUCKET']
        self.aws_profile = config['AWS_PROFILE']
        self.local_dir = config['DIR_PUBLISH']
        self.local_dir_abs = str(pathlib.Path(config['DIR_PUBLISH']).resolve()) + '/'
        self.exclude_from_upload = config['EXCLUDE_FROM_UPLOAD']
        self.ignore_on_server = config['IGNORE_ON_SERVER']
        self.dry_run = args.dry_run
        self.puncts = re.compile('[%s]' % re.escape(string.punctuation))
        self.use_gzip = config['S3_USE_GZIP']
        self.gzip_compression_level = config['S3_GZIP_COMPRESSION']
        self.gzip_file_extensions = config['S3_GZIP_FILES']
        self.gzip_minsize = config['S3_GZIP_MINSIZE']
        self.cloudfront_id = None
        if 'CLOUDFRONT_ID' in os.environ:
            self.cloudfront_id = os.environ['CLOUDFRONT_ID']


    def deploy(self):
        print("Deploying site to S3 bucket: {}".format(self.s3_bucket))
        session = boto3.session.Session(profile_name=self.aws_profile)
        client = session.client('s3')

        local_files = self.get_local_files()
        remote_files = self.get_remote_files(client)
        newfiles = self.get_new_files(local_files, remote_files)
        updated = self.get_updated_files(local_files, remote_files)
        oldfiles = self.get_old_files(local_files, remote_files)

        print("\nUploading {} new files to S3...".format(str(len(newfiles))))
        for f in newfiles:
            self.upload_file(newfiles[f], client)

        print("\nModifying {} existing files on S3...".format(str(len(updated))))
        for f in updated:
            self.upload_file(updated[f], client)

        print("\nDeleting {} old files from S3...".format(str(len(oldfiles))))
        for f in oldfiles:
            self.delete_from_s3(oldfiles, client)

        remote_actions = len(newfiles) + len(updated) + len(oldfiles)
        if remote_actions > 0 and not self.dry_run and self.cloudfront_id is not None:
            self.invalidate_cloudfront(session)


    def get_local_files(self):
        paths = pathlib.Path(self.local_dir).glob('**/*')
        files = {}
        for p in paths:
            if p.is_file():
                key = to_uri(p, self.local_dir_abs)
                val = {
                    'localpath': p,
                    'LastModified': to_date(p.stat().st_mtime),
                    'Size': p.stat().st_size,
                    'ETag': md5(p)
                }
                files[key] = val
        return keysort(files)


    def get_remote_files(self, client):
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.s3_bucket)
        files = {}
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objdict = {
                        'LastModified': obj['LastModified'],
                        'Size': obj['Size'],
                        'ETag': self.remove_puncts(obj['ETag'])
                    }
                    files[obj['Key']] = objdict
        return keysort(files)


    def get_new_files(self, local, remote):
        newfiles = {}
        for f in local:
            if f not in remote and not pattern_match(f, self.exclude_from_upload):
                newfile = {
                    'key': f,
                    'localpath': local[f]['localpath']
                }
                if self.needs_gzip(local[f]):
                    zippedpath = compress_copy(local[f]['localpath'], self.gzip_compression_level)
                    newfile['zippedpath'] = zippedpath
                newfiles[f] = newfile
        return newfiles


    def needs_gzip(self, localfile):
        if not self.use_gzip:
            return False

        with open(localfile['localpath'], 'rb') as test_f:
            already_gzipped = test_f.read(2) == b'\x1f\x8b'

        if already_gzipped:
            return False

        if int(localfile['Size']) >= self.gzip_minsize and pattern_match(localfile['localpath'].name, self.gzip_file_extensions):
            return True
        else:
            return False


    def get_updated_files(self, local, remote):
        updated = {}
        for f in local:
            if f in remote and not pattern_match(f, self.ignore_on_server):
                is_modified = False
                zippedpath = None
                if self.needs_gzip(local[f]):
                    zippedpath = compress_copy(local[f]['localpath'], self.gzip_compression_level)
                    if md5(zippedpath) != remote[f]['ETag']:
                        is_modified = True
                else:
                    if local[f]['ETag'] != remote[f]['ETag']:
                        is_modified = True
                if is_modified:
                    updated[f] = {
                        'key': f,
                        'localpath': local[f]['localpath']
                    }
                    if zippedpath is not None:
                        updated[f]['zippedpath'] = zippedpath
        return updated


    def get_old_files(self, local, remote):
        oldfiles = []
        for f in remote:
            if f not in local and not pattern_match(f, self.ignore_on_server):
                oldfiles.append(f)
        return oldfiles


    def upload_file(self, file, client):
        local_filename = file['localpath'].resolve()
        remote_key = file['key']
        mimetype, _ = mimetypes.guess_type(local_filename)
        if mimetype is None:
            mimetype = "application/octet-stream"
        metadata = {
            "ContentType": mimetype
        }
        upload_filename = local_filename
        if 'zippedpath' in file:
            upload_filename = file['zippedpath'].resolve()
            metadata['ContentEncoding'] = "gzip"

        print("{}\t{}".format(remote_key, metadata))

        if not self.dry_run:
            client.upload_file(
                Filename=str(upload_filename),
                Bucket=self.s3_bucket,
                Key=remote_key,
                ExtraArgs=metadata
            )


    def delete_from_s3(self, filelist, client):
        if len(filelist) == 0:
            return
        deletedict = get_object_dict(filelist)
        for f in filelist:
            print(f)
        if not self.dry_run:
            client.delete_objects(Bucket=self.s3_bucket, Delete=deletedict)


    def invalidate_cloudfront(self, session):
        client = session.client('cloudfront')
        ts = datetime.datetime.utcnow()
        print("Creating Cloudfront invalidation with caller reference: ", str(ts))
        response = client.create_invalidation(
            DistributionId=self.cloudfront_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        '/*'
                    ],
                },
                'CallerReference': str(ts)
            }
        )
        pprint.pprint(response)


    def remove_puncts(self, s):
        return self.puncts.sub('', s)

