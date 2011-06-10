# -*- coding: utf-8 -*-
"""

@startuml


skinparam sequenceLifeLineBackgroundColor #FFBBBB

actor alice
alice -> comm...message: save()\nstate: NEW
activate comm...message 
comm...message -> ecsmail.utils: deliver
activate ecsmail.mail 
ecsmail.mail -->> ecsmail.tasks: queue_send
activate ecsmail.tasks 
ecsmail.mail -> comm...message:msgid,\nraw_message
deactivate ecsmail.mail
comm...message -> comm...message: msgid:\nstate:PENDING
deactivate comm...message
ecsmail.tasks -->> comm...tasks: msgid,\nstate:STARTED
activate comm...tasks 
comm...tasks --> comm...message: update state
deactivate comm...tasks
ecsmail.tasks -> django.core.mail: send message
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
    django.core.mail -> ecsmail.tasks
    deactivate django.core.mail 
    ecsmail.tasks -->> comm...tasks: msgid,\nstate:SUCCESS
    deactivate ecsmail.tasks 
    activate comm...tasks 
    comm...tasks --> comm...message: update state
    deactivate comm...tasks

else transfer temporary Failure [3 retries]
    activate smartmx
    activate django.core.mail
    activate ecsmail.tasks
     
    smartmx -> django.core.mail: temporary Failure
    deactivate smartmx
    django.core.mail -> ecsmail.tasks
    deactivate django.core.mail 
    ecsmail.tasks -->> comm...tasks: msgid,\nstate:RETRY 
    activate comm...tasks 
    comm...tasks --> comm...message: update state
    deactivate comm...tasks
    ecsmail.tasks -> django.core.mail: send message
    activate django.core.mail 
    django.core.mail -> smartmx: smtp transfer
    activate smartmx 

else transfer permanent Failure
    smartmx -> django.core.mail: permanent Failure
    deactivate smartmx
    django.core.mail -> ecsmail.tasks
    deactivate django.core.mail 
    ecsmail.tasks -->> comm...tasks: msgid,\nstate:FAILURE
    deactivate ecsmail.tasks 
    activate comm...tasks 
    comm...tasks --> comm...message: update state
    deactivate comm...tasks
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