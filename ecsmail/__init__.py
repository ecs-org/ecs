# -*- coding: utf-8 -*-
"""
@startuml
world -> ecs.ecsmail.server: smtp
ecs.ecsmail.server -> ecs.communication.mailreceiver: settings.ECSMAIL ['handlers']
@enduml

@startuml
world -> ecs.ecsmail.server: smtp
ecs.ecsmail.server -> ecs.communication.mailreceiver: settings.ECSMAIL ['handlers']
@enduml

"""