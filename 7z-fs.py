#!/usr/bin/python3

import os, sys, errno

import sh
from sh import sevenz

from fuse import FUSE, FuseOSError, Operations

from utiltools import shellutils as shu

#sh.sudo('ln -s /usr/bin/7z /usr/bin/sevenz')

def parse_7z_list_names(out):
   lines = out.split('\n')

   names_started = False

   fnames = []

   for line in lines:
      if '----' in line:
         if not names_started:
            names_started = True
            continue
         else:
            break
      if names_started:
         words = line.split(' ')
         if len(words) > 0:
            fnames.append(words[-1])
      pass

   return fnames


def parse_7z_list(out):
   lines = out.split('\n')

   names_started = False

   files = []

   for line in lines:

      if '----' in line:
         if not names_started:
            names_started = True
            continue
         else:
            break
         pass

      if names_started:

         words = list(filter(lambda x: x!='', line.split(' ')))
         #print(words)

         if len(words) > 0:
            fdata = {}

            fdata['date'] = words[0]
            fdata['time'] = words[1]
            fdata['attr'] = words[2]
            fdata['size'] = int(words[3])
            fdata['compressed'] = int(words[4])
            fdata['name'] = words[-1]

            files.append(fdata)
            pass

         pass

      pass

   return files


def mk_tmp():
   rand_str = shu.rand_str(10)
   tmp_path = '/tmp/7z_fs/tmp_' + rand_str
   shu.mkdir(tmp_path)
   return tmp_path


class SevenZipFs(Operations):

   def __init__(self, root):
      root = root.replace('.7z', '') + '.7z'

      self.root = root
      self.tmp_path = mk_tmp()

      if shu.file_exists(root):
         sh.sevenz('a', root, '.empty_file')
      pass

   def access(self, path, mode):
      pass
   def chmod(self, path, mode):
      pass
   def chown(self, path, uid, gid):
      pass

   def getattr(self, path, fh=None):
      out = sh.sevenz('l', self.root)
      flist = parse_7z_list(out)
      return {
         #'st_mtime' : flist[0]['time'],
         'st_atime' : 0,
         'st_ctime' : 0,
         'st_mtime' : 0,

         'st_size' : flist[0]['size'],
      }


   def readdir(self, path, fh):
      out = sh.sevenz('l', self.root)
      dirents = parse_7z_list_names(out)
      #for r in dirents:
      #   yield r
      return dirents

   def unlink(self, path):
      print(path)
      #sh.sevenz('d',

   #File methods
   def read(self, path, length, offset, fh):
      pass

def main(mountpoint, root):
   FUSE(SevenZipFs(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
   main(sys.argv[2], sys.argv[1])
