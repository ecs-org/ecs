from django.dispatch import Signal

on_document_download = Signal() # sender=Document kwargs: document, user
