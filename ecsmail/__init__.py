# -*- coding: utf-8 -*-
"""

@startuml


skinparam sequenceLifeLineBackgroundColor #FFBBBB

actor alice
alice -> comm...message: save()\nstate: NEW
activate comm...message 
comm...message -> ecsmail.mail: deliver
activate ecsmail.mail 
ecsmail.mail -->> ecsmail.task_queue: queue_send
activate ecsmail.task_queue 
ecsmail.mail -> comm...message:msgid,\nraw_message
deactivate ecsmail.mail
comm...message -> comm...message: msgid:\nstate:PENDING
deactivate comm...message
ecsmail.task_queue -->> comm...task_queue: msgid,\nstate:STARTED
activate comm...task_queue 
comm...task_queue --> comm...message: update state
deactivate comm...task_queue
ecsmail.task_queue -> django.core.mail: send message
activate django.core.mail 
django.core.mail -> smartmx: smtp transfer
activate smartmx 

alt transfer OK
    smartmx -> django.core.mail: OK
    smartmx -->> targetmx: smtp transfer
    deactivate smartmx
    activate targetmx 
    actor bob
    targetmx -->> bob: read mail
    deactivate targetmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> comm...task_queue: msgid,\nstate:SUCCESS
    deactivate ecsmail.task_queue 
    activate comm...task_queue 
    comm...task_queue --> comm...message: update state
    deactivate comm...task_queue

else transfer temporary Failure [3 retries]
    activate smartmx
    activate django.core.mail
    activate ecsmail.task_queue
     
    smartmx -> django.core.mail: temporary Failure
    deactivate smartmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> comm...task_queue: msgid,\nstate:RETRY 
    activate comm...task_queue 
    comm...task_queue --> comm...message: update state
    deactivate comm...task_queue
    ecsmail.task_queue -> django.core.mail: send message
    activate django.core.mail 
    django.core.mail -> smartmx: smtp transfer
    activate smartmx 

else transfer permanent Failure
    smartmx -> django.core.mail: permanent Failure
    deactivate smartmx
    django.core.mail -> ecsmail.task_queue
    deactivate django.core.mail 
    ecsmail.task_queue -->> comm...task_queue: msgid,\nstate:FAILURE
    deactivate ecsmail.task_queue 
    activate comm...task_queue 
    comm...task_queue --> comm...message: update state
    deactivate comm...task_queue
@enduml


@startuml
skinparam sequenceLifeLineBackgroundColor #FFBBBB

Actor Bob
Bob --> homemx: smtp transfer
activate homemx
homemx --> ecsmail.server: smtp transfer
activate ecsmail.server
ecsmail.server -> comm...mailhandler
activate comm...mailhandler
@enduml
    
    


"""