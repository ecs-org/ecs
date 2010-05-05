import random, itertools, math
from celery.decorators import task
from ecs.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation

def optimize_random(timetable, func):
    p = list(timetable)
    random.shuffle(p)
    return p
    
def optimize_brute_force(timetable, func):
    value, p = max((func(p), p) for p in itertools.permutations(timetable))
    return p
    
def optimize_ga(timetable, func):
    sorter = GeneticSorter(timetable, func, seed=(timetable,), population_size=100, crossover_p=0.3, mutations={
        inversion_mutation: 0.002,
        swap_mutation: 0.02,
        displacement_mutation: 0.01,
    })
    return sorter.run(100)

_OPTIMIZATION_ALGORITHMS = {
    'random': optimize_random,
    'brute_force': optimize_brute_force,
    'ga': optimize_ga,
}

def _eval_timetable(metrics):
    return 1000*1000 * (1.0 / (metrics._waiting_time_total + 1)) + 1000.0 / (metrics.constraint_violation_total + 1) + 1000.0 / (math.sqrt(metrics._optimal_start_diff_squared_sum) + 1)

@task()
def optimize_timetable_task(meeting=None, algorithm=None):
    retval = False
    try:
        algo = _OPTIMIZATION_ALGORITHMS.get(algorithm)
        entries, users = meeting.timetable
        f = meeting.create_evaluation_func(_eval_timetable)
        meeting._apply_permutation(algo(entries, f))
        retval = True
    finally:
        meeting.optimization_task_id = None
        meeting.save()

    return retval
