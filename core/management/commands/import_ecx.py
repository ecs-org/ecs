from django.core.management.base import BaseCommand
from ecs.core.serializer import Serializer

class Command(BaseCommand):
    def handle(self, file, **options):
        serializer = Serializer()
        with open(file, 'rb') as f:
            serializer.read(f)
