import random
from django.test import TestCase

from ecs.utils.genetic_sort import GeneticSorter, swap_mutation

class GeneticSorterTest(TestCase):
    '''Tests for the GeneticSorter module
    
    Genetic sorting tests.
    '''
    
    def test_list_sort(self):
        '''Tests if the GeneticSorter correctly sorts a supplied list.
        '''
        
        N = 20
        data = random.sample(xrange(N), N)
        f = lambda p: sum(1.0 / (abs(i-x) + 1) for i, x in enumerate(p))
        sorter = GeneticSorter(data, evaluation_func=f, population_size=50, mutations={swap_mutation: 0.02})
        # This is fragile: if we don't find a solution in 10^6 generations this test will fail.
        for i in xrange(1000):
            result = sorter.run(1000)
            if result == tuple(xrange(N)):
                break
        self.failUnlessEqual(result, tuple(xrange(N)))
        