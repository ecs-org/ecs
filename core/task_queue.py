import random, itertools, math, subprocess
from celery.decorators import task
from haystack import site

from ecs.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation
from ecs.core.models import Meeting, Document, Page


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
def optimize_timetable_task(meeting_id=None, algorithm=None, **kwargs):
    logger = optimize_timetable_task.get_logger(**kwargs)
    meeting = Meeting.objects.get(id=meeting_id)
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

@task()
def extract_and_index_pdf_text(document_pk=None, **kwargs):
    logger = extract_and_index_pdf_text.get_logger(**kwargs)
    logger.debug("indexing doc %s" % document_pk)
    try:
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return
    if not doc.pages or doc.mimetype != 'application/pdf':
        logger.info("Warning, doc.pages (%s) not set or doc.mimetype (%s) != 'application/pdf'" % (str(doc.pages), str(doc.mimetype)))
        return
    for p in xrange(1, doc.pages + 1):
        cmd = ["pdftotext", "-raw", "-nopgbrk", "-enc", "UTF-8", "-eol", "unix", "-f", "%s" % p,  "-l",  "%s" % p,  "-q", doc.file.path, "-"]
        popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text, stderr = popen.communicate()
        doc.page_set.create(num=p, text=text)
        # FIXME: as a delayed tasks there ist missing error handling
    index = site.get_index(Page)
    index.backend.update(index, doc.page_set.all())
    
    