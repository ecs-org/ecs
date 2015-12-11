import subprocess
import os
import tempfile
import shutil
from datetime import datetime
from contextlib import contextmanager

from django.conf import settings

from ecs.pki.models import Certificate, CertificateAuthority


CONF_TEMPLATE = '''
[ ca ]
default_ca  = CA_default

[ CA_default ]
private_key = {workdir}/ca.key.pem
certificate = {ca_root}/ca.cert.pem

database    = {workdir}/index.txt
serial      = {workdir}/serial
crlnumber   = {workdir}/crlnumber
new_certs_dir = {workdir}

default_md   = sha1
preserve     = no
policy       = policy_any
default_days = 730
default_bits = 2048

[ policy_any ]
countryName            = supplied
stateOrProvinceName    = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional
'''


@contextmanager
def _workdir():
    workdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(workdir, 'openssl-ca.cnf'), 'w') as f:
            f.write(CONF_TEMPLATE.format(
                ca_root=settings.ECS_CA_ROOT, workdir=workdir))

        with open(os.path.join(workdir, 'index.txt'), 'w') as f:
            now = datetime.now()
            for cert in Certificate.objects.order_by('serial'):
                status = 'V'
                exp_ts = cert.expires_at.strftime('%y%m%d%H%M%SZ')
                rev_ts = ''
                serial = '{:02x}'.format(cert.serial)
                if cert.revoked_at:
                    status = 'R'
                    rev_ts = cert.revoked_at.strftime('%y%m%d%H%M%SZ')
                elif cert.expires_at < now:
                    status = 'E'

                f.write('\t'.join([
                    status, exp_ts, rev_ts, serial, 'unknown', cert.subject,
                ]))
                f.write('\n')

        ca = CertificateAuthority.objects.get()
        with open(os.path.join(workdir, 'ca.key.pem'), 'w') as f:
            f.write(ca.key)

        yield workdir
    finally:
        shutil.rmtree(workdir)


def _exec(cmd):
    return subprocess.check_output(['openssl'] + cmd)


def _get_cert_data(cert):
    out = _exec([
        'x509', '-noout', '-in', cert, '-serial', '-dates', '-subject',
    ])
    data = dict(line.split('=', 1) for line in out.rstrip('\n').split('\n'))
    return {
        'serial': int(data['serial'], 16),
        'created_at': datetime.strptime(
            data.pop('notBefore'), '%b %d %H:%M:%S %Y %Z'),
        'expires_at': datetime.strptime(
            data.pop('notAfter'), '%b %d %H:%M:%S %Y %Z'),
        'subject': data['subject'].strip(),
    }


def setup(subject):
    assert not CertificateAuthority.objects.exists()

    key = _exec(['genrsa', '2048'])

    p = subprocess.Popen([
        'openssl', 'req', '-batch', '-new', '-key', '/dev/stdin', '-x509',
        '-days', '3650', '-subj', subject,
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    cert, err = p.communicate(key)
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, 'openssl')

    CertificateAuthority.objects.create(key=key, cert=cert)


def make_cert(subject, pkcs12_file, days=None, passphrase=''):
    with _workdir() as workdir:
        with open(os.path.join(workdir, 'serial'), 'w') as f:
            f.write('{:02x}'.format(Certificate.get_serial()))

        key_file = os.path.join(workdir, 'key.pem')
        csr_file = os.path.join(workdir, 'x.csr')
        cert_file = os.path.join(workdir, 'cert.pem')

        # generate a key and a certificate signing request
        _exec(['genrsa', '-out', key_file])
        _exec([
            'req', '-batch', '-new', '-key', key_file, '-out', csr_file,
            '-subj', subject,
        ])

        # sign the request
        to_be_signed = [
            'ca', '-batch', '-config', os.path.join(workdir, 'openssl-ca.cnf'),
            '-in', csr_file, '-out', cert_file,
        ]
        if days:
            to_be_signed += ['-days', str(days)]
        _exec(to_be_signed)

        # create a browser compatible certificate
        _exec([
            'pkcs12', '-export', '-clcerts', '-in', cert_file,
            '-inkey', key_file, '-out', pkcs12_file,
            '-passout', 'pass:{}'.format(passphrase),
        ])
        return _get_cert_data(cert_file)


def gen_crl():
    with _workdir() as workdir:
        with open(os.path.join(workdir, 'crlnumber'), 'w') as f:
            f.write('{:02x}'.format(Certificate.get_crlnumber()))

        crl_path = os.path.join(settings.ECS_CA_ROOT, 'crl.pem')

        _exec([
            'ca', '-batch', '-config', os.path.join(workdir, 'openssl-ca.cnf'),
            '-gencrl', '-crldays', '3650', '-out', crl_path,
        ])
