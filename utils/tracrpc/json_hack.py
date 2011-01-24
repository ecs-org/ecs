# -*- coding: utf-8 -*-
'''
Created on Sep 22, 2010

@author: scripty
'''

from jsonrpclib.jsonclass import *
from datetime import datetime

#from jsonrpclib import jsonrpc
from jsonrpclib import MultiCall
from jsonrpclib.jsonrpc import *

class MultiCall_agilo(MultiCall):
    def _request(self):
        if len(self._job_list) < 1:
            # Should we alert? This /is/ pretty obvious.
            return

        request_body = {'method': 'system.multicall', 'params':
                        [job.request_non_dump() for job in self._job_list]
                        , 'id': 233}
        request_body = jdumps(request_body)
        
        #request_body = '[ %s ]' % ','.join([job.request() for
        #                                  job in self._job_list])
        
        responses = self._server._run_request(request_body)
        del self._job_list[:]
        if not responses:
            responses = []
        return MultiCallIterator(responses)
    
    __call__ = _request

jsonrpclib.MultiCall_agilo = MultiCall_agilo

def request_non_dump(self, encoding=None, rpcid=None):
        return {'method':self.method, 'params': self.params, 'jsonrpc': 2.0, 'id':random_id() if rpcid is None else rpcid}

MultiCallMethod.request_non_dump = request_non_dump

def monkey_load(obj):
    #print "MY monkeyload"
    if type(obj) in string_types+numeric_types+value_types:
        return obj
    if type(obj) is types.ListType:
        return_list = []
        for entry in obj:
            return_list.append(monkey_load(entry))
        return return_list
    # Othewise, it's a dict type
    if '__jsonclass__' not in obj.keys():
        return_dict = {}
        for key, value in obj.iteritems():
            new_value = monkey_load(value)
            return_dict[key] = new_value
        return return_dict
    # It's a dict, and it's a __jsonclass__
    orig_module_name = obj['__jsonclass__'][0]
    params = obj['__jsonclass__'][1]
    if orig_module_name == '':
        raise TranslationError('Module name empty.')
    json_module_clean = re.sub(invalid_module_chars, '', orig_module_name)
    if json_module_clean != orig_module_name:
        raise TranslationError('Module name %s has invalid characters.' %
                               orig_module_name)
    json_module_parts = json_module_clean.split('.')
    json_class = None
    if len(json_module_parts) == 1:
        # Local class name -- probably means it won't work
        if json_module_parts[0] not in config.classes.keys():
            raise TranslationError('Unknown class or module %s.' %
                                   json_module_parts[0])
        json_class = config.classes[json_module_parts[0]]
    else:
        json_class_name = json_module_parts.pop()
        json_module_tree = '.'.join(json_module_parts)
        print "json_module_tree: %s" % json_module_tree
        try:
            temp_module = __import__(json_module_tree)
        except ImportError:
            raise TranslationError('Could not import %s from module %s.' %
                                   (json_class_name, json_module_tree))
        json_class = getattr(temp_module, json_class_name)
    # Creating the object...
    new_obj = None
    #print "json_class: '%s' " % str(json_class)
    
    
    if type(params) is types.ListType:
        new_obj = json_class(*params)
    elif type(params) is types.DictType:
        new_obj = json_class(**params)
    elif str(json_class) == "<class '__main__.datetime'>":
        #FIXME this is just ugly but works for now
        #new_obj = datetime(params)
        new_obj = datetime.strptime(params, "%Y-%m-%dT%H:%M:%S")
    elif type(json_class) == type(datetime):
        #import pdb; pdb.set_trace()
        new_obj = datetime.strptime(params, "%Y-%m-%dT%H:%M:%S")
    else:
        #print "json_class: %s" % json_class
        #print "type(json_class): %s" % type(json_class)
        #print "params: %s" % params
        raise TranslationError('Constructor args must be a dict or list.')
    for key, value in obj.iteritems():
        if key == '__jsonclass__':
            continue
        setattr(new_obj, key, value)
    return new_obj

#monkeypatching:
import jsonrpclib.jsonclass
jsonrpclib.jsonclass.load = monkey_load
