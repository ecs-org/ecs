from ecs.utils import connect
from ecs.documents.models import DownloadHistory
from ecs.documents import signals

@connect(signals.on_document_download)
def on_vote_published(sender, **kwargs):
    document = kwargs['document']
    user = kwargs['user']
    DownloadHistory.objects.create(document=document, user=user)
