# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#
"""
Unittests for the site
"""


class BasicImportTests():
    """Tests for most basic importability of core modules
    """
    
    def test_import(self,):
        """Tests if settings and urls modules are importable. Simple but quite useful.
        """
        
        import settings
        import urls


