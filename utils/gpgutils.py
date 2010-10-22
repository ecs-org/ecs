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

def reset_keystore(gpg_home):
    for f in os.listdir(gpg_home):
        path = os.path.join(gpg_home, f);
        if os.path.isfile(path):
            os.remove(path)

def import_key(filelike, gpg_home):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s --homedir %s --batch --yes --import %s' % (GPG_EXECUTABLE, gpg_home, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d' % (returncode))
   
def encrypt(filelike, gpg_home, owner):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s --homedir %s --batch --yes --always-trust -r %s --output %s --encrypt %s' % (GPG_EXECUTABLE, gpg_home, owner, tmp_out, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d' % (returncode))
    
    return open(tmp_out, 'rb')

def decrypt(filelike, gpg_home, owner):
    tmp_in, tmp_out = _prepare(filelike)
    args = '%s --homedir %s --batch --yes --always-trust -r %s --output %s --decrypt %s' % (GPG_EXECUTABLE, gpg_home, owner, tmp_out, tmp_in)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT ,shell=True)
    returncode = popen.wait()
    
    if returncode != 0:
        raise IOError('gpg returned error code:%d' % (returncode))
    
    return open(tmp_out, 'rb')
