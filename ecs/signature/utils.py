import random
from functools import wraps
from datetime import timedelta
import urllib.request, urllib.parse, urllib.error

from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.core.urlresolvers import reverse

def _total_seconds(td): # work around python < 2.7
    return float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

class SigningData(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None

    def _gen_id(self):
        return '%s' % random.randint(1, int(1e17) - 1)

    @classmethod
    def retrieve(cls, id):
        data = cache.get(id)
        if not data is None:
            data = cls(data)
            data.id = id
        return data

    def store(self, **kwargs):
        if not self.id:
            self.id = self._gen_id()
        timeout = None
        if kwargs:
            timeout = int(_total_seconds(timedelta(**kwargs)))
        cache.set(self.id, dict(self), timeout)

    def delete(self):
        if self.id:
            cache.delete(self.id)

    def pop_listitem(self, key, index):
        item = self[key].pop(0)
        self.store()
        return item


def with_sign_data(data=True, session=False):
    def _outer(func):
        @wraps(func)
        def _inner(request, *args, **kwargs):
            pdf_id = request.GET.get('pdf-id', kwargs.pop('pdf_id', None))
            request.sign_data = SigningData.retrieve(pdf_id)
            if not request.sign_data and data:
                raise Http404('Invalid pdf-id. Probably your signing session expired. Please retry.')
            request.sign_session = SigningData.retrieve(kwargs.pop('sign_session_id', None) or request.sign_data.get('sign_session_id'))
            if not request.sign_session and session:
                raise Http404('Invalid sign_session_id. Probably your signing session expired. Please retry.')
            return func(request, *args, **kwargs)
        return _inner
    return _outer


def get_pdfas_url(request, sign_data):
    values = {
        'connector': request.user.profile.signing_connector,
        'invoke-app-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_receive', kwargs={'pdf_id': sign_data.id})),
        'invoke-app-url-target': '_top',
        'invoke-app-error-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_error', kwargs={'pdf_id': sign_data.id})),
        'locale': 'DE',
        'num-bytes': str(len(sign_data['pdf_data'])),
        'sig_type': 'SIGNATURBLOCK_DE',
        'pdf-url': request.build_absolute_uri(reverse('ecs.signature.views.sign_send', kwargs={'pdf_id': sign_data.id})),

        'verify-level': 'intOnly', # Dies bedeutet, dass eine Signaturprüfung durchgeführt wird, allerdings ohne Zertifikatsprüfung.
        'filename': sign_data['document_filename'],

        #'preview': 'false',
        #'mode': 'binary',
        #'inline': 'false',
        #'pdf-id': sign_data.id,
    }
    data = urllib.parse.urlencode({k: v.encode('utf-8') for k, v in values.items()})
    return '{0}Sign?{1}'.format(settings.PDFAS_SERVICE, data)
