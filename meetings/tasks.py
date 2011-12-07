import random, itertools, math, os, time
from datetime import timedelta
from celery.decorators import task, periodic_task

from django.conf import settings

from ecs.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation, random_replacement_mutation
from ecs.meetings.models import Meeting


def optimize_random(timetable, func, params):
    p = list(timetable)
    random.shuffle(p)
    return p
    
def optimize_brute_force(timetable, func, params):
    value, p = max((func(p), p) for p in itertools.permutations(timetable))
    return p
    
def optimize_ga(timetable, func, params):
    params = params or {}
    population_size = params.get('population_size', 100)
    sorter = GeneticSorter(timetable, func, seed=(timetable,), population_size=population_size, crossover_p=0.2, mutations={
        inversion_mutation: 0.005,
        swap_mutation: 0.05,
        displacement_mutation: 0.03,
        random_replacement_mutation: 0.01,
    })
    return sorter.run(params.get('iterations', 100))

_OPTIMIZATION_ALGORITHMS = {
    'random': optimize_random,
    'brute_force': optimize_brute_force,
    'ga': optimize_ga,
}

_log2 = math.log(2)

def _eval_timetable(metrics):
    v = 0.0 # badness
    v += metrics._waiting_time_total / 10800.0 # 1 ~ 3h waiting
    v += 2 * math.pow(metrics.constraint_violation_total, 2)
    v += metrics._optimal_start_diff_squared_sum / 3240000.0
    return math.log(1 + 1.0 / (1 + v)) / _log2

@task()
def optimize_timetable_task(meeting_id=None, algorithm=None, algorithm_parameters=None, **kwargs):
    logger = optimize_timetable_task.get_logger(**kwargs)
    meeting = Meeting.objects.get(id=meeting_id)
    retval = False
    try:
        algo = _OPTIMIZATION_ALGORITHMS.get(algorithm)
        entries, users = meeting.timetable
        batch_entries = []
        regular_entries = []
        for entry in entries:
            if entry.is_batch_processed:
                batch_entries.append(entry)
            else:
                regular_entries.append(entry)

        head, body, tail = (), regular_entries, ()
        for index, entry in enumerate(reversed(regular_entries)):
            if entry.submission_id:
                if index:
                    tail = tuple(regular_entries[-index:])
                    body = body[:-index]
                break
        for index, entry in enumerate(regular_entries):
            if entry.submission_id:
                if index:
                    head = tuple(regular_entries[:index])
                    body = body[index:]
                break

        f = meeting.create_evaluation_func(_eval_timetable)
        meeting._apply_permutation(head + algo(tuple(body), f, algorithm_parameters) + tail + tuple(batch_entries))
        retval = True
    except Exception, e:
        logger.error("meeting optimization error (pk=%s, algo=%s): %r" % (meeting_id, algorithm, e))
    finally:
        print Meeting.objects.filter(pk=meeting_id).update(optimization_task_id=None)

    return retval


@periodic_task(run_every=timedelta(seconds=3)) #24*60*60
def cull_zip_cache():
    logger = cull_zip_cache.get_logger()
    logger.info("culling download cache")
    for path in os.listdir(settings.ECS_DOWNLOAD_CACHE_DIR):
        if path.startswith('.'):
            continue
        path = os.path.join(settings.ECS_DOWNLOAD_CACHE_DIR, path)
        age = time.time() - os.path.getmtime(path)
        if age > settings.ECS_DOWNLOAD_CACHE_MAX_AGE:
            os.remove(path)
            