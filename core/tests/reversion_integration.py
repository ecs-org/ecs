#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#
"""
This module contains unit tests that demonstrate the usage of the Reversion storage.
"""

from ecs.core import models
import reversion, datetime
from reversion.models import Version

class TestReversion:
    def setUp(self):
        with reversion.revision:
            d1 = models.Document(uuid_document="test", uuid_document_revision="test2", date=datetime.date.today(), version="version")
            reversion.revision.comment = "Initial and only version."
            d1.save()
            self.d1 = d1
    
    def test_list_of_versions(self):
        version_list = Version.objects.get_for_object(self.d1)
        assert len(version_list) == 1
        assert version_list[0].object_repr == 'Document object'

    def test_new_version(self):
        with reversion.revision:
            self.d1.version = "version2"
            self.d1.save()
            reversion.revision.comment = "Well, usually our models are write once, but for this we need to change it"
        
        version_list = Version.objects.get_for_object(self.d1)
        assert len(version_list) == 2
        assert version_list[0].object_repr == 'Document object'
        assert version_list[1].revision.comment.startswith("Well")
        assert version_list[0].revision.comment.startswith("Init")

        #from reversion.helpers import generate_patch
        #patch = generate_patch(version_list[0], version_list[1], "content")
        
