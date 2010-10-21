'''
Created on Sep 16, 2010
 
@author: elchaschab
'''
import tempfile
import subprocess
import os
from django.conf import settings
from ecs.utils.pathutils import which

GPG_EXECUTABLE =  settings.ECS_GNUPG if hasattr(settings,"ECS_GNUPG") else which('gpg').next()

def _prepare(filelike):
    tmp_dir = tempfile.mkdtemp() 
    tmp_in = os.path.join(tmp_dir, 'in')
    tmp_out = os.path.join(tmp_dir, 'out')
             
    f_in = open(tmp_in, "wb");
    if hasattr(filelike, 'read'):
        f_in.write(filelike.read())
    else:
        f_in.write(filelike)
    f_in.close();
    return tmp_in, tmp_out

def import_key(filelike):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s --batch --yes --import %s' % (GPG_EXECUTABLE, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d %s' % (returncode, popen.stderr.read()))
   
# FIXME: make encrypt working and change to symmetric key
def encrypt(filelike, owner):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s  --batch --yes --always-trust -r %s --output %s --encrypt %s' % (GPG_EXECUTABLE, owner, tmp_out, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d %s' % (returncode, popen.stderr.read()))
    
    return open(tmp_out, 'rb')

# FIXME: make decrypt working change to symmetric key
def decrypt(filelike, owner):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s  --batch --yes --always-trust -r %s --output %s --decrypt %s' % (GPG_EXECUTABLE, owner, tmp_out, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d %s' % (returncode, popen.stderr.read()))
    
    return open(tmp_out, 'rb')
