import sys
import importlib
from xml.dom.minidom import parse
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from StringIO import StringIO



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', action='store', dest='outfile', help='output file', default=None),
        make_option('-i', action='store', dest='infile', help='input file', default=None),
    )
    def handle(self, test, **options):
        
        if not options['outfile']:
            print "no output file specified!"
            return
        if not options['infile']:
            print "no input file specified!"
            return
        
        #FIXME
        print "DEBUG FIXME for workflow model to import 'test' must be in sys.argv at import time:"
        print "test in sys.argv:", 'test' in sys.argv
        #parse it
        
        dom1 = parse(options['infile'])
        cases = {}
        for testcase in dom1.firstChild.childNodes:
            cname = testcase.attributes.getNamedItem('classname').value
            if not cases.has_key(cname):
                cases[cname] = {}
                cases[cname]['tests'] = []
            
            case = {'failed':False,
                    'errors': [],
                    }
            
            for k in testcase.attributes.keys():
                case[k] = testcase.attributes.getNamedItem(k).value
            
            
            #TODO
            #check if testcase has child nodes "error" or "failure"
            if testcase.hasChildNodes():
                for child in testcase.childNodes:
                    if child.tagName == 'error':
                        derror = {}
                        for k in child.attributes.keys():
                            derror[k] = child.attributes.getNamedItem(k).value
                        derror['traceback'] = child.childNodes[0].wholeText
                        case['errors'].append(derror)
                    elif child.tagName == 'failure':
                        dfailure = {}
                        for k in child.attributes.keys():
                            dfailure[k] = child.attributes.getNamedItem(k).value
                        dfailure['traceback'] = child.childNodes[0].wholeText
                        case['failure'] = dfailure
                        case['failed'] = True
                    else:
                        print "unhandled testcase child tag in",cname, case['name']
            
            
            cases[cname]['tests'].append(case)
               
            """< error type="exceptio
ameError" message="global name 'bla' is not defined"><![CDATA[Traceback (most recent call last):
  File "/usr/lib/python2.6/unittest.py", line 279, in run
    testMethod()
  File "/scratch/wuxxin/src/ecs/../ecs/utils/tests/gpgutils.py", line 84, in testError
    blu = bla
NameError: global name 'bla' is not defined
]]></error>"""
            
            """<failure typ
xceptions.AssertionError" message="1 != 0"><![CDATA[Traceback (most recent call last):
  File "/usr/lib/python2.6/unittest.py", line 279, in run
    testMethod()
  File "/scratch/wuxxin/src/ecs/../ecs/utils/tests/gpgutils.py", line 82, in testFail
    self.assertEqual(1,0)
  File "/usr/lib/python2.6/unittest.py", line 350, in failUnlessEqual
    (msg or '%r != %r' % (first, second))
AssertionError: 1 != 0
]]></failure>"""
            
            
        
        
        for pclassname, casedict in cases.iteritems():
            tests = casedict['tests'] 
            module_doc = ""
            impname = pclassname[:pclassname.rindex('.')]
            classname = pclassname[pclassname.rindex('.')+1:]
            
            try:
                m=importlib.import_module(impname)
                module_doc = m.__doc__
                
                try:
                    c=getattr(m, classname)
                    cases[pclassname]['docstring'] = c.__doc__
                    for test in tests:
                        t=getattr(c, test['name'])
                        test['docstring'] = t.__doc__
                    
                    
                except AttributeError,ae:
                    #FIXME what's different for ecs.tests that it doesn't work?
                    if impname == 'ecs' and classname ==  'tests':
                        print "FIXME: cannot import ecs.tests for unknown reason..."
                        for test in tests:
                            if not test.has_key('docstring'):
                                test['docstring'] = ''
                                print pclassname,test['name'], 'docstring is missing'
                    else:
                        raise AttributeError(ae)
                    
                
                if not cases[pclassname].has_key('docstring'):
                    cases[pclassname]['docstring']=''
                    print pclassname, "docstring is missing"
                
                    
            except ImportError,ie:
                
                print " ",ImportError,ie
                print " ",classname,"failed"
                pass

        
        testcases2rst(cases, outfile=options['outfile'])
        print ""
        print "done"

        
def testcases2rst(cases, outfile, one_case_per_page=True):
    '''dumps testcase data from hudson mixed in with docstrings to a single file'''
    import codecs
    if not cases:
        print "no testcase data to dump"
        return
    """
        for each xml entry:
      * while classname is same:
        * write "General Testdescription: " part of uit-tmp-1 (Module, Description (=.__doc__)
          e.g.: module=ecs.integration.tests.BootstrapTestCase, description = eval(ecs.integration.tests.BootstrapTestCase.__doc__)
        * for each test:
          * write TestcaseID, docstring, failed/passed, time
        """
    
    out = []
    for pclassname, casedict in cases.iteritems():
        
        tests = casedict['tests']
        
        out.append("{0}".format(pclassname) )
        out.append("#"*len(pclassname) )
        out.append("")
        out.append("General Testdescription:")
        out.append("")
        out.append("Tested Module: {0}".format(pclassname))
        out.append("")
        out.append("Description: {0}".format(casedict['docstring']))
        out.append("")
        out.append("")
        for test in tests:
            out.append(' - {0}.{1}, {2}, {3}, {4}sec'.format(pclassname,test['name'], test['docstring'], 'FAILED' if test['failed'] else 'PASSED', test['time']))
        out.append("")
        out.append("")
        if one_case_per_page:
            out.append(".. raw:: latex")
            out.append("")
            out.append("   \pagebreak")
            out.append("   \\newpage")
            out.append("")
            out.append("")
    
    fd = codecs.open(outfile, 'wb', encoding='utf-8')
    fd.write('\n'.join(out))
    fd.close()
    
    
    
    
    
    
