from django.dispatch import Signal

workflow_started = Signal()
workflow_finished = Signal()
token_created = Signal()
token_consumed = Signal()
token_unlocked = Signal()
deadline_reached = Signal()
activity_performed = Signal()