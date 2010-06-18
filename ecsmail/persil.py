import re
import BeautifulSoup
from BeautifulCleaner.bc import clean

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

def whitewash(htmltext):
    doc = BeautifulSoup.BeautifulSoup(htmltext)
    clean(doc)
    for el in doc.findAll():
        removeElement(el)
    string = unicode(doc)
    string = '\n\n'.join(re.split(r'\s*\n\s*\n\s*', string))
    string = re.sub('\s\s\s+', ' ', string)
    string = wrap(string, 70)
    return string