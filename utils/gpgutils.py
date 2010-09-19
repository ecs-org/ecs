'''
Created on Sep 16, 2010
 
@author: elchaschab
'''
import tempfile
import subprocess
import os

def _prepare(filelike):
    tmp_dir = tempfile.mkdtemp() 
    tmp_in = os.path.join(tmp_dir, 'in')
    tmp_out = os.path.join(tmp_dir, 'out')
             
    f_in = open(tmp_in, "wb");
    f_in.write(filelike);
    f_in.close();
    return tmp_in, tmp_out

# TODO change to symmetric key
def encrypt(filelike, fingerprint):
    tmp_in, tmp_out = _prepare(filelike)

    args = '/usr/bin/gpg --always-trust --batch --yes -r %s --output %s --encrypt %s' % (fingerprint, tmp_out, tmp_in)
    popen = subprocess.Popen(args, shell=True)

    if popen.returncode != 0:
        raise IOError('gpg returned error code % i')
    
    return open(tmp_out, 'rb')

# TODO change to symmetric key
def decrypt(filelike, fingerprint):
    tmp_in, tmp_out = _prepare(filelike)

    args = '/usr/bin/gpg --always-trust --batch --yes -r %s --output %s --decrypt %s' % (fingerprint, tmp_out, tmp_in)
    popen = subprocess.Popen(args, shell=True)

    if popen.returncode != 0:
        raise IOError('gpg returned error code % i')
    
    return open(tmp_out, 'rb')
