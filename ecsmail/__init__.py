# -*- coding: utf-8 -*-
"""

@startuml


skinparam sequenceLifeLineBackgroundColor #FFBBBB

actor alice
alice -> communication.message: save()\nstate: NEW
activate communication.message 
communication.message -> ecsmail.mail: deliver
activate ecsmail.mail 
ecsmail.mail -->> ecsmail.task_queue: queue_send
activate ecsmail.task_queue 
ecsmail.mail -> communication.message: msg_ids, raw_message
deactivate ecsmail.mail
deactivate communication.message
ecsmail.task_queue -->> communication.task_queue: msgid, state:PENDING
activate communication.task_queue 
communication.task_queue --> communication.message: update state
deactivate communication.task_queue
ecsmail.task_queue -> django.core.mail: send message
activate django.core.mail 
django.core.mail -> smartmx: smtp transfer
activate smartmx 
alt transfer OK
    smartmx -> django.core.mail: OK
    smartmx -->> targetmx: transfer mail
    deactivate smartmx
    activate targetmx 
    actor bob
    targetmx -->> bob: read mail
    deactivate targetmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> communication.task_queue: msgid, state:SUCCESS
    deactivate ecsmail.task_queue 
    activate communication.task_queue 
    communication.task_queue --> communication.message: update state
    deactivate communication.task_queue
else transfer temporary Failure [3 retries]
    activate smartmx
    activate django.core.mail
    activate ecsmail.task_queue
     
    smartmx -> django.core.mail: TEMPORARY FAILURE
    deactivate smartmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> communication.task_queue: msgid, state:RETRY 
    activate communication.task_queue 
    communication.task_queue --> communication.message: update state
    deactivate communication.task_queue
    ecsmail.task_queue -> django.core.mail: send message
    activate django.core.mail 
    django.core.mail -> smartmx: smtp transfer
    activate smartmx 

else transfer permanent Failure
    smartmx -> django.core.mail: PERMANENT FAILURE
    deactivate smartmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> communication.task_queue: msgid, state:FAILURE
    deactivate ecsmail.task_queue 
    activate communication.task_queue 
    communication.task_queue --> communication.message: update state
    deactivate communication.task_queue
@enduml

"""