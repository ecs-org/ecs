# -*- coding: utf-8 -*-
"""

@startuml
skin BlueModern


actor user
user -> communication.message: save()
activate communication.message
communication.message -> ecsmail.mail: send_mail
activate ecsmail.mail
ecsmail.mail -->> ecsmail.task_queue: queue_send
activate ecsmail.task_queue
ecsmail.mail -> communication.message: msg_ids, raw_message
deactivate ecsmail.mail
deactivate communication.message
ecsmail.task_queue -->> communication.task_queue: msgid, state:pending
activate communication.task_queue
communication.task_queue --> communication.message: update state
deactivate communication.task_queue
ecsmail.task_queue -> smartmx: send message
activate smartmx
smartmx -> ecsmail.task_queue: 200 OK
deactivate smartmx
ecsmail.task_queue -->> communication.task_queue: msgid, state:success
deactivate ecsmail.task_queue 
activate communication.task_queue
communication.task_queue --> communication.message: update state
deactivate communication.task_queue
@enduml

"""