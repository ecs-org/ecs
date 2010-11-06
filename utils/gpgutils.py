# -*- coding: utf-8 -*-

import os, subprocess
from django.conf import settings
from ecs.utils.pathutils import which

GPG_EXECUTABLE =  settings.ECS_GNUPG if hasattr(settings,"ECS_GNUPG") else which('gpg').next()


def reset_keystore(gpghome):
    if not os.path.isdir(gpghome):
        os.makedirs(gpghome)
    for f in os.listdir(gpghome):
        path = os.path.join(gpghome, f);
        if os.path.isfile(path):
            os.remove(path)

def import_key(keyfile, gpghome):
    args = [GPG_EXECUTABLE, '--homedir' , gpghome, '--batch', '--yes', '--import', keyfile]
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --import returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
   
def encrypt(sourcefile, destfile,  gpghome, owner):
    args = [GPG_EXECUTABLE, '--homedir', gpghome, '--batch', '--yes', '--always-trust', 
            '-r', owner, '--output', destfile , '--encrypt', sourcefile] 
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --encrypt returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
    
def decrypt(sourcefile, destfile, gpghome, owner):
    args = [GPG_EXECUTABLE, '--homedir', gpghome, '--batch', '--yes', '--always-trust', 
            '-r', owner, '--output', destfile, '--decrypt', sourcefile] 
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --decrypt returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
