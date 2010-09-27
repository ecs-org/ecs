import imp
from django.conf import settings
from django.utils.importlib import import_module
from django.db.models.signals import post_save, class_prepared
from django.contrib.contenttypes.models import ContentType

from ecs.workflow.controllers import Activity, FlowController, guard

__all__ = ('Activity', 'FlowController', 'NodeController', 'register', 'guard', 'autostart_disabled')

_registered_models = set()
_autostart_disabled = False

def register(model):
    if model in _registered_models:
        return
    _registered_models.add(model)
    from ecs.workflow.descriptors import WorkflowDescriptor
    model.workflow = WorkflowDescriptor()
    
def autodiscover():
    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue
        try:
            imp.find_module('workflow', app_path)
        except ImportError:
            continue
        module = import_module("%s.workflow" % app)

def _post_save(sender, **kwargs):
    if _autostart_disabled or sender not in _registered_models:
        return
    # XXX: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299 (FMD1)
    if kwargs['created'] and not kwargs.get('raw'):
        from ecs.workflow.models import Workflow, Graph
        ct = ContentType.objects.get_for_model(sender)
        graphs = Graph.objects.filter(content_type=ct, auto_start=True)
        for graph in graphs:
            wf = Workflow.objects.create(graph=graph, data=kwargs['instance'])
            wf.start()
post_save.connect(_post_save)


# HACK
from django.utils.functional import wraps
import warnings

class _AutostartDisabled(object):
    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return decorated
    
    def __enter__(self):
        globals()['_autostart_disabled'] = True

    def __exit__(self, exc_type, exc_value, traceback):
        globals()['_autostart_disabled'] = False

def autostart_disabled():
    warnings.warn("Disabling workflow autostart is not thread safe", UserWarning, stacklevel=2)
    return _AutostartDisabled()

    
    