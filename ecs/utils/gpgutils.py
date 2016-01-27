"""
==================
ecs.utils.gpgutils
==================

Encryption/Signing, Decryption/Verifying modul.

- This module uses Gnu Privacy Guard for the actual encryption work

  - The GNU Privacy Guard -- a free implementation of the OpenPGP standard as defined by RFC4880
  - GnuPG is GPL licensed
  - Usage in ecs: via commandline wrapper
"""

import os, subprocess, tempfile, re
import shutil


def reset_keystore(gpghome):
    ''' wipes out keystore under directory gpghome

    :warn: deletes every file in this directory
    '''
    if not os.path.isdir(gpghome):
        os.makedirs(gpghome)
    for f in os.listdir(gpghome):
        path = os.path.join(gpghome, f);
        if os.path.isfile(path):
            os.remove(path)


def gen_keypair(ownername, secretkey_filename, publickey_filename):
    ''' writes a pair of ascii armored key files, first is secret key, second is publickey, minimum ownername length is five'''

    gpghome = tempfile.mkdtemp()

    batch_args = "Key-Type: 1\nKey-Length: 2048\nExpire-Date: 0\nName-Real: {0}\n".format(ownername)
    batch_args += "%secring {0}\n%pubring {1}\n".format(secretkey_filename, publickey_filename)
    batch_args += "%commit\n%echo done\n"

    args = ['gpg', '--homedir' , gpghome, '--batch', '--armor', '--yes', '--gen-key']
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, empty = popen.communicate(batch_args)
    popen.stdin.close()
    shutil.rmtree(gpghome)
    if popen.returncode != 0:
        raise IOError('gpg --gen-key returned error code: %d , cmd line was: %s , output was: %s' % (popen.returncode, str(args), stdout))


def import_key(keyfile, gpghome):
    ''' import a keyfile (generated by gen_keypair) into gpghome directory gpg keyring '''
    args = ['gpg', '--homedir' , gpghome, '--batch', '--yes', '--import', keyfile]
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, empty = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        raise IOError('gpg --import returned error code: %d , cmd line was: %s , output was: %s' % (returncode, str(args), stdout))


def encrypt_sign(sourcefile, destfile, gpghome, encrypt_owner, signer_owner=None):
    ''' read sourcefile, encrypt and optional sign and write destfile

    :param gpghome: directory where the .gpg files are
    :param encrypt_owner: owner name of key for encryption using his/her public key
    :param signer_owner: if not None: owner name of key for signing using his/her secret key
    '''
    cmd = [
        'gpg', '--homedir', gpghome, '--batch', '--yes', '--always-trust',
        '--recipient', encrypt_owner, '--output', destfile,
    ]
    if signer_owner:
        cmd += ['--local-user', signer_owner, '--sign']
    cmd += ['--encrypt']

    subprocess.check_call(cmd, stdin=sourcefile)


def decrypt_verify(sourcefile, gpghome, decrypt_owner, verify_owner=None):
    ''' read sourcefile, decrypt and optional verify if signer is verify_owner

    :param decrypt_owner: owner name of key used for decryption using his/her secret key
    :param verify_owner: owner name of key used for verifying that it was signed using his/her public key
    :raise IOError: on gnupg error, with detailed info
    :raise KeyError: if key owner could not be verified
    '''
    destfile = tempfile.TemporaryFile()
    cmd = [
        'gpg', '--homedir', gpghome, '--batch', '--yes', '--always-trust',
        '--recipient', decrypt_owner, '--decrypt', sourcefile,
    ]
    p = subprocess.Popen(cmd, stdout=destfile, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)

    if verify_owner is not None:
        err = err.decode('utf-8')
        m = re.search(r'gpg: Good signature from "([^"]*)"', err)
        if not m or not m.group(1) == verify_owner:
            raise KeyError('could not verify that signer was keyowner: {} , cmd line was: {} , output was: {}'.format(verify_owner, cmd, err))

    destfile.seek(0)
    return destfile