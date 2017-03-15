import random, itertools, math
import io
import zipfile

from celery.task import task, periodic_task
from celery.schedules import crontab

from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ecs.utils.genetic_sort import GeneticSorter, inversion_mutation, swap_mutation, displacement_mutation, random_replacement_mutation
from ecs.meetings.models import Meeting
from ecs.checklists.models import Checklist
from ecs.documents.models import Document


def optimize_random(timetable, func, params):
    p = list(timetable)
    random.shuffle(p)
    return tuple(p)
    
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
    v += metrics._waiting_time_total.total_seconds() / 10800.0 # 1 ~ 3h waiting
    v += 2 * math.pow(metrics.constraint_violation_total, 2)
    v += metrics._optimal_start_diff_squared_sum / 3240000.0
    return math.log(1 + 1.0 / (1 + v)) / _log2

@task()
@transaction.atomic
def optimize_timetable_task(meeting_id=None, algorithm=None, algorithm_parameters=None):
    logger = optimize_timetable_task.get_logger()
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
    except Exception as e:
        logger.error("meeting optimization error (pk=%s, algo=%s): %r" % (meeting_id, algorithm, e))
    finally:
        Meeting.objects.filter(pk=meeting_id).update(optimization_task_id=None)

    return retval


@task()
@transaction.atomic
def render_protocol_pdf(meeting_id=None, user_id=None):
    meeting = Meeting.objects.get(id=meeting_id)

    try:
        meeting.render_protocol_pdf()
    finally:
        meeting.protocol_rendering_started_at = None
        meeting.save(update_fields=('protocol_rendering_started_at',))


@periodic_task(run_every=crontab(hour=4, minute=7))
def gen_meeting_zip():
    try:
        meeting = Meeting.objects.next()
    except Meeting.DoesNotExist:
        return

    checklist_ct = ContentType.objects.get_for_model(Checklist)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for submission in meeting.submissions(manager='unfiltered').all():
            sf = submission.current_submission_form

            docs = []
            if sf.pdf_document:
                docs.append(sf.pdf_document)
            docs += sf.documents.filter(doctype__identifier='patientinformation')
            docs += Document.objects.filter(
                content_type=checklist_ct,
                object_id__in=submission.checklists.filter(status='review_ok'),
            )

            path = [
                submission.get_workflow_lane_display(),
                submission.get_filename_slice(),
            ]
            for doc in docs:
                zf.writestr('/'.join(path + [doc.get_filename()]),
                    doc.retrieve_raw().read())

    if meeting.documents_zip:
        meeting.documents_zip.delete()

    meeting.documents_zip = Document.objects.create_from_buffer(
        zip_buf.getvalue(), doctype='meeting_zip', parent_object=meeting,
        mimetype='application/zip', name=meeting.title)
    meeting.save(update_fields=('documents_zip',))
