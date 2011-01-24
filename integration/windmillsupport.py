# -*- coding: utf-8 -*-
import os
from .functional import wraps # copied from django 1.2.3 into integration, to get rid of django dependencies
   
from windmill.authoring import WindmillTestClient
from windmill.bin.admin_lib import configure_global_settings, process_options, setup


def windmill_run(browser, command, targettest=None, targethost=None, *args):   
    wmargs = list(args)
    if command == "run":
        wmargs = ['windmill', '-e', 'run_service', 'test='+ targettest, browser, targethost] + wmargs
    elif command == "shell":
        wmargs = ['windmill', 'shell', browser, targethost] + wmargs
    else:
        print("Invalid parameter line, use either run or shell")
        return False
    
    import sys
    import windmill    
    windmill.stdout, windmill.stdin = sys.stdout, sys.stdin
    inject_firefox_plugins()
    print "wmargs", wmargs    
    configure_global_settings()
    action = process_options(wmargs)
    shell_objects = setup() 
    return action(shell_objects)


## decorators ##

def logged_in(username='windmill@example.org', password='shfnajwg9e'):
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            client = WindmillTestClient(fn.__name__)
            
            client.click(id=u'id_username')
            client.type(text=username, id=u'id_username')
            client.click(id=u'id_password')
            client.type(text=password, id=u'id_password')
            client.click(value=u'login')
            client.waits.forPageLoad(timeout=u'20000')

            try:
                rval = fn(client, *args, **kwargs)
            finally:
                try:
                    client.waits.forElement(link=u'Logout', timeout=u'8000')
                    client.click(link=u'Logout')
                    client.waits.forPageLoad(timeout=u'20000')
                finally:
                    client.execJS(js='var element=document.createElement("CookieCleaner"); document.documentElement.appendChild(element); var evt=document.createEvent("Events"); evt.initEvent("UploadAssistantDeleteCookies", true, false); element.dispatchEvent(evt);')
                    client.execJS(js='window.location.href = "/";')
                    client.waits.forPageLoad(timeout=u'20000')
                    client.execIDEJS(js="""fleegix.fx.fadeOut($('ideForm')); d= function() {$('ideForm').innerHTML = '';windmill.ui.recorder.recordOff(); fleegix.fx.fadeIn($('ideForm')); }; setTimeout("d()", 800);""")

            return rval

        return decorated

    return decorator
    

def anonymous():
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            client = WindmillTestClient(fn.__name__)
            
            return fn(client, *args, **kwargs)
        return decorated
    return decorator


## HACK: dont look at this ##
def inject_firefox_plugins():
    from windmill.dep._mozrunner import get_moz as get_moz_orig
    
    def get_moz(*args, **kwargs):
        plugins = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'windmill', 'uploadassistant.xpi')]
        kwargs['settings']['MOZILLA_PLUGINS'] = kwargs['settings'].get('MOZILLA_PLUGINS', []) + plugins
        return get_moz_orig(*args, **kwargs)

    from windmill.dep import _mozrunner
    _mozrunner.get_moz = get_moz

# HACK: work around nose / windmill issue
def monkey_mozrunner():
    def monkey_patched_mozrunner_run_command(cmd, env=None):
        """Run the given command in killable process."""
        if hasattr(sys.stdout, 'fileno'):
           kwargs = {'stdout':sys.stdout, 'stderr':sys.stderr, 'stdin':sys.stdin}
        else:
           kwargs = {'stdout':sys.__stdout__ ,'stderr':sys.__stderr__, 'stdin':sys.stdin}
    
        if sys.platform != "win32":
            return killableprocess.Popen(cmd, preexec_fn=lambda: os.setpgid(0, 0), env=env, **kwargs)
        else:
            return killableprocess.Popen(cmd, **kwargs) 
    
    from windmill.dep import _mozrunner
    _mozrunner.run_command = monkey_patched_mozrunner_run_command
