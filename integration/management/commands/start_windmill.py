#   Copyright (c) 2008-2009 Mikeal Rogers <mikeal.rogers@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = "Run windmill tests. Specify a browser (eg. firefox, chrome)"

    args = 'browser <label label ...>'
    label = 'label'

    def handle(self, *args, **kwargs):

        import sys
        from pkg_resources import load_entry_point

        sys.argv = ['windmill', 'shell',] + list(args)

        sys.exit(
            load_entry_point('windmill==1.4', 'console_scripts', 'windmill')()
        )


