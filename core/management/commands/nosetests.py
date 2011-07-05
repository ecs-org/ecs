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
            
            case = {}
            for k in testcase.attributes.keys():
                case[k] = testcase.attributes.getNamedItem(k).value
            cases[cname]['tests'].append(case)
        
        
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
            out.append(' - {0}.{1}, {2}, failed?/passed?, {3}sec'.format(pclassname,test['name'], test['docstring'], test['time']))
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
    
    
    
    
    
    
