import random, math, time
from itertools import izip

def order_crossover(perm_a, perm_b): # OX
    n = len(perm_a)
    i, j = random.sample(xrange(n), 2)
    if j < i:
        i, j = j, i
    if i == j:
        return perm_a, perm_b
    a_slice, b_slice = perm_a[i:j], perm_b[i:j]
    a_compl, b_compl = tuple(x for x in perm_b if not x in a_slice), tuple(x for x in perm_a if not x in b_slice)
    return a_compl[:i] + a_slice + a_compl[i:], b_compl[:i] + b_slice + b_compl[i:]

def swap_mutation(perm):
    i, j = random.sample(xrange(len(perm)), 2)
    perm = list(perm)
    perm[i], perm[j] = perm[j], perm[i]
    return tuple(perm)
    
def inversion_mutation(perm):
    i, j = random.sample(xrange(len(perm)), 2)
    if j < i:
        i, j = j, i
    return perm[:i] + tuple(reversed(perm[i:j])) + perm[j:]
    
def displacement_mutation(perm):
    n = len(perm)
    i, j = random.sample(xrange(n), 2)
    if i == j:
        return perm
    if j < i:
        i, j = j, i
    rest = perm[:i] + perm[j:]
    k = random.randint(0, n - j + i)
    return rest[:k] + perm[i:j] + rest[k:]
    

class GeneticSorter(object):
    def __init__(self, data, evaluation_func=None, seed=None, population_size=None, crossover_p=0.3, mutations=None):
        self.data = data
        self.evaluation_func = evaluation_func
        self.n = len(data)
        self.population_size = population_size
        self.population = list(seed or [])
        for i in xrange(population_size - len(self.population)):
            self.population.append(self.random_permutation())
        self.evaluation = {}
        self.min_value = None
        self.max_value = None
        self.avg_value = None
        self.best_permutation = None
        self.crossover_p = crossover_p
        self.generation_count = 0
        self.total_time = 0
        self.time_per_generation = 0
        if mutations:
            self.mutations = mutations.items()
        else:
            self.mutations = ()
        self.evaluate()
        
    def evaluate(self):
        self.evaluation = {}
        sum_value = 0.0
        for permutation in self.population:
            value = self.evaluation_func(permutation)
            self.evaluation[id(permutation)] = value
            sum_value += value
            if self.max_value is None or value > self.max_value:
                self.max_value = value
                self.best_permutation = permutation
            if self.min_value is None or value < self.min_value:
                self.min_value = value
        self.avg_value = sum_value / len(self.population)
        self.sum_value = sum_value
        
    def random_permutation(self):
        return tuple(random.sample(self.data, self.n))
        
    def crossover(self, perm_a, perm_b):
        return order_crossover(perm_a, perm_b)
        
    def run(self, max_generations=None, threshold=None):
        generation = 0
        starttime = time.time()
        while True:
            self.next_generation()
            generation += 1
            if max_generations and generation >= max_generations:
                break
            if threshold and threshold <= self.max_value:
                break
            if self.min_value == self.max_value:
                break
        self.total_time += time.time() - starttime
        self.time_per_generation = self.total_time / self.generation_count
        return self.best_permutation

    def next_generation(self):
        next_population = []
        wheel = []
        for permutation in self.population:
            value = self.evaluation[id(permutation)]
            fitness = value / self.avg_value
            fitness_fraction, copies = math.modf(fitness)
            if fitness_fraction:
                wheel.append(permutation)
                wheel.append(permutation)
            if copies == 1:
                next_population.append(permutation)
            elif copies > 1:
                next_population += [permutation] * int(copies)

        # XXX: fractional copies should be placed with a proportinal probability (FMD2)
        next_population += random.sample(wheel, len(self.population) - len(next_population))
        next_population_size = len(next_population)

        # crossover
        crossover_count = int(0.5 * self.crossover_p * next_population_size)
        crossover_indices = random.sample(xrange(next_population_size), 2 * crossover_count)
        for i in xrange(crossover_count):
            index_a, index_b = crossover_indices[2*i], crossover_indices[2*i+1]
            next_population[index_a], next_population[index_b] = self.crossover(next_population[index_a], next_population[index_b])
        
        # mutation
        for mutation, p in self.mutations:
            for index in random.sample(xrange(next_population_size), int(p * next_population_size)):
                next_population[index] = mutation(next_population[index])
        
        self.population = next_population
        self.generation_count += 1
        self.evaluate()

