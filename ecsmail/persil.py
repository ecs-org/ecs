import re
import copy
import BeautifulSoup
from BeautifulCleaner.bc import clean, removeElement

# http://code.activestate.com/recipes/148061/
def wrap(text, width):
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def whitewash(htmltext, puretext=True):
    if puretext:
        hexentityMassage = copy.copy(BeautifulSoup.BeautifulSoup.MARKUP_MASSAGE)
        hexentityMassage = [(re.compile('&#x([^;]+);'), 
            lambda m: '&#%d' % int(m.group(1), 16))]

        doc = BeautifulSoup.BeautifulSoup(htmltext,
            convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES,
            markupMassage=hexentityMassage)        
    else:
        doc = BeautifulSoup.BeautifulSoup(htmltext)
        
    clean(doc)
    for el in doc.findAll():
        removeElement(el)
    string = unicode(doc)
    string = '\n\n'.join(re.split(r'\s*\n\s*\n\s*', string))
    string = re.sub('\s\s\s+', ' ', string)
    string = wrap(string, 70)
    return string