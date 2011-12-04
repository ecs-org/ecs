# -*- coding: utf-8 -*-

from ecs.utils import Args

checklist_questions = {
    u'thesis_review': [
        Args('1', u'Geben Sie eine positive Empfehlung ab?'),  # XXX: dont change this number
    ],
    u'statistic_review': [
        Args('1', u'Ist das Studienziel ausreichend definiert?'),
        Args('2', u'Ist das Design der Studie geeignet, das Studienziel zu erreichen?'),
        Args('3', u'Ist die Studienpopulation ausreichend definiert?'),
        Args('4', u'Sind die Zielvariablen geeignet definiert?'),
        Args('5', u'Ist die statistische Analyse beschrieben, und ist sie adäquat?'),
        Args('6', u'Ist die Größe der Stichprobe ausreichend begründet?'),
    ],
    u'legal_review': [
        Args( '1', u"Anrede: entspricht?"),
        Args( '2', u"Hinweis auf Freiwilligkeit: entspricht?"),
        Args( '3', u"Hinweis auf jederzeitigen Abbruch: entspricht?"),
        Args( '4', u"Schwangerschaftspassus: entspricht?"),
        Args( '5', u"Versicherungspassus: entspricht?"),
        Args( '6', u"Name und Erreichbarkeit des Prüfarztes: entspricht?"),
        Args( '7', u"Hinweis auf Patientenanwaltschaft: entspricht?"),
        Args( '8', u"Vermeidung von Fremdwörtern: entspricht?"),
        Args( '9', u"Rechtschreibung und Grammatik: entspricht?"),
        Args('10', u"Die Patienteninformation entspricht in allen anderen Punkten den Anforderungen?"),
    ],
    u'insurance_review': [
        Args('1', u"Sind die Angaben zu Versicherung vollständig und adäquat?"),
    ],
    u'external_review': [
        Args('1a', u'Ist die Ausarbeitung des Projektes hinreichend um es begutachten zu können?', requires_comment=True),
        Args('1b', u'Ist das Projekt vollständig (inkl. Angaben über Nebenwirkungen etc.)?',
            description=u'Bitte beurteilen Sie in diesem Zusammenhang auch die Vollständigkeit und Richtigkeit der in der Kurzfassung enthaltenen Aufstellung der studienbezogenen Maßnahmen!', requires_comment=True),
        Args('2',  u'Ist die Fragestellung des Projektes relevant?', requires_comment=True),
        Args('3',  u'Ist die angewandte Methodik geeignet, die Fragestellung zu beantworten?', requires_comment=True),
        Args('3a', u'Findet sich im Protokoll eine Begründung der gewählten Fallzahl und eine Angabe über die geplante statistische Auswertung?', requires_comment=True),
        Args('4a', u'Werden den Patienten/Probanden durch das Projekt besondere Risken zugemutet?',
            description=u'''- durch eine neue Substanz mit hoher Nebenwirkungsrate
            - durch Vorenthalten einer wirksamen Therapie
            - durch radioaktive Isotope
            - durch eine spezielle Dosierung von Medikamenten''', is_inverted=True, requires_comment=True),
        Args('4b', u'Stehen diese Risken Ihrer Meinung nach in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie?', requires_comment=True),
        Args('5a', u'Werden dem Patienten/Probanden durch die für die Studie notwendigen Untersuchungen besondere Belastungen bzw. Risken zugemutet?', is_inverted=True, requires_comment=True),
        Args('5b', u'Stehen diese Belastungen in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie ?', requires_comment=True),
        Args('6',  u'Liegt ein Patienteninformationsblatt bei? Ist dieses ausreichend und verständlich?'),
        Args('7a', u'Haben sie einen „conflict of interest“ offenzulegen?',
            description=u'''Die Ethik-Kommission der Medizinischen Universität Wien ist bemüht sicherzustellen, dass alle, die am Begutachtungsverfahren für eines der eingereichten Projekte teilnehmen, die Möglichkeit haben, etwaige Sachverhalte und Interessen, die eine objektive Begutachtung hindern können, anzugeben. Dies können finanzielle sowie akademische Interessen sein. Die Gutachter werden ersucht, Stellung zu nehmen und Interessen offen zu legen.''', is_inverted=True),
        Args('7b', u'Erklären Sie, dass Sie alle Informationen, die Sie im Namen dieser Begutachtung erhalten habe, vertraulich behandlen?'),
    ],
    u'gcp_review': [
        Args( '1', u'Sind die Allgemeinen Informationen ausreichend und korrekt angegeben?'),
        Args( '2', u'Sind die Hintergrundinformationen ausreichend und korrekt angegeben?'),
        Args( '3', u'Ist das Studienziel und der Studienzweck detailliert beschrieben?'),
        Args( '4', u'Ist das Studiendesign ausreichend dargelegt? (Endpunkte, Studienphase, Bias-Vermeidung, Prüfpräparat, Labelling, Dauer, Beendigung, Accountability, Randomisierung, Source Daten)'),
        Args( '5', u'Sind Patientenauswahl und Austritts- bzw. Abbruchkriterien ausreichend definiert? (Ein-/Ausschluss, Abbruch, Datenerhebung, follow up, Ersatz)'),
        Args( '6', u'Ist die Behandlung der Studienteilnehmer, samt erlaubter/nicht erlaubter Medikation und Überprüfungsverfahren ausreichend definiert?'),
        Args( '7', u'Sind die Efficacy Parameter sowie Methoden, zeitliche Planung und Erfassung & Analyse d. Efficacy Parameter ausreichend definiert?'),
        Args( '8', u'Ist Safety und Safety Reporting Parameter ausreichend definiert, und adäquat?'),
        Args( '9', u'Sind die Angaben zur statistischen Datenerhebung, -Auswertung, -Methoden ausreichend und adäquat?'),
        Args('10', u'Ist die Qualitätskontrolle und Qualitätssicherung ausreichend beschrieben und sind diese Angaben adäquat?'),
        Args('11', u'Sind Angaben zu ethischen Aspekten vorhanden?'),
        Args('12', u'Sind Angaben zu Datenerhebung, Dokumentation und Verarbeitung ausreichend definiert und sind diese adäquat?'),
        Args('13', u'Sind Angaben zu Finanzierung und Versicherung ausreichend definiert und sind diese adäquat?'),
        Args('14', u'Sind Angaben zur Regelung bzgl Publikation ausreichend definiert?'),
        Args('15', u'Anhang, wenn zutreffend?'),
    ],
    u'boardmember_review': [
        Args('1', u"Ist das Antragsformular korrekt und vollständig ausgefüllt?"),
        Args('2', u"Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“ der MedUni Wien?"),
        Args('3', u"Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?"),
    ],
    u'expedited_review': [
        Args('1', u'Geben Sie eine positive Empfehlung ab?', requires_comment=True),  # XXX: dont change this number
        Args('2', u"Ist das Antragsformular korrekt und vollständig ausgefüllt?", requires_comment=True),
        Args('3', u"Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“ der MedUni Wien?", requires_comment=True),
        Args('4', u"Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?"),
    ],
    u'localec_review': [
        Args('1', u'Die Ethik-Kommission bestätigt als lokale Ethik-Kommission im Sinne des §41b (5) die Eignung der Prüfer, seiner Mitarbeiter und die Angemessenheit der Einrichtungen in ihrem Zuständigkeitsbereich.'),     # XXX: dont change this number
    ],
}
