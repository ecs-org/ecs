# -*- coding: utf-8 -*-
"""
==================
ecs.utils.gpgutils
==================

Encryption/Signing, Decryption/Verifying modul.

 - This module uses Gnu Privacy Guard for the actual encryption work
 
------------------
third-party: GnuPg
------------------

 - The GNU Privacy Guard -- a free implementation of the OpenPGP standard as defined by RFC4880 
 - GnuPG is licensed 


"""

import os, subprocess
from django.conf import settings
from ecs.utils.pathutils import which

GPG_EXECUTABLE =  settings.ECS_GNUPG if hasattr(settings,"ECS_GNUPG") else which('gpg').next()


def reset_keystore(gpghome):
    ''' wipes out keystore under directory gpghome; Warning: deletes every file in this directory ''' 
    if not os.path.isdir(gpghome):
        os.makedirs(gpghome)
    for f in os.listdir(gpghome):
        path = os.path.join(gpghome, f);
        if os.path.isfile(path):
            os.remove(path)

def gen_keypair(ownername):
    ''' Returns a tuple of amored strings, first is secret key, second is publickey'''
    return NotImplementedError
 
def import_key(keyfile, gpghome):
    args = [GPG_EXECUTABLE, '--homedir' , gpghome, '--batch', '--yes', '--import', keyfile]
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --import returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
   
def encrypt_sign(sourcefile, destfile,  gpghome, owner, recipient):
    args = [GPG_EXECUTABLE, '--homedir', gpghome, '--batch', '--yes', '--always-trust', 
            '-r', owner, '--output', destfile , '--encrypt', sourcefile] 
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --encrypt returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
    
def decrypt_verify(sourcefile, destfile, owner, sender):
    args = [GPG_EXECUTABLE, '--homedir', gpghome, '--batch', '--yes', '--always-trust', 
            '-r', owner, '--output', destfile, '--decrypt', sourcefile] 
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --decrypt returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))
