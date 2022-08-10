from ecs.utils import Args

checklist_questions = {
    'thesis_review': [
        Args('1', 'Handelt es sich um eine retrospektive Diplomstudie und geben Sie eine positive Empfehlung ab?'),  # XXX: dont change this number
    ],
    'statistic_review': [
        Args('1', 'Ist das Studienziel ausreichend definiert?'),
        Args('2', 'Ist das Design der Studie geeignet, das Studienziel zu erreichen?'),
        Args('3', 'Ist die Studienpopulation ausreichend definiert?'),
        Args('4', 'Sind die Zielvariablen geeignet definiert?'),
        Args('5', 'Ist die statistische Analyse beschrieben, und ist sie adäquat?'),
        Args('6', 'Ist die Größe der Stichprobe ausreichend begründet?'),
    ],
    'legal_review': [
        Args('1', 'Entspricht die Patienteninformation in allen Punkten den Anforderungen?'),
    ],
    'insurance_review': [
        Args('1', "Sind die vorgelegten Unterlagen zur Versicherung vollständig und akzeptabel?"),
    ],
    'external_review': [
        Args('1a', 'Ist die Ausarbeitung des Projektes hinreichend um es begutachten zu können?', requires_comment=True),
        Args('1b', 'Ist das Projekt vollständig (inkl. Angaben über Nebenwirkungen etc.)?',
            description='Bitte beurteilen Sie in diesem Zusammenhang auch die Vollständigkeit und Richtigkeit der in der Kurzfassung enthaltenen Aufstellung der studienbezogenen Maßnahmen!', requires_comment=True),
        Args('2',  'Ist die Fragestellung des Projektes relevant?', requires_comment=True),
        Args('3',  'Ist die angewandte Methodik geeignet, die Fragestellung zu beantworten?', requires_comment=True),
        Args('3a', 'Findet sich im Protokoll eine Begründung der gewählten Fallzahl und eine Angabe über die geplante statistische Auswertung?', requires_comment=True),
        Args('4a', 'Werden den Patienten/Probanden durch das Projekt besondere Risken zugemutet?',
            description='''- durch eine neue Substanz mit hoher Nebenwirkungsrate
            - durch Vorenthalten einer wirksamen Therapie
            - durch radioaktive Isotope
            - durch eine spezielle Dosierung von Medikamenten''', is_inverted=True, requires_comment=True),
        Args('4b', 'Stehen diese Risken Ihrer Meinung nach in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie?', requires_comment=True),
        Args('5a', 'Werden dem Patienten/Probanden durch die für die Studie notwendigen Untersuchungen besondere Belastungen bzw. Risken zugemutet?', is_inverted=True, requires_comment=True),
        Args('5b', 'Stehen diese Belastungen in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie ?', requires_comment=True),
        Args('6',  'Liegt ein Patienteninformationsblatt bei? Ist dieses ausreichend und verständlich?'),
        Args('7a', 'Haben sie einen „conflict of interest“ offenzulegen?',
            description='''Die Ethik-Kommission ist bemüht sicherzustellen, dass alle, die am Begutachtungsverfahren für eines der eingereichten Projekte teilnehmen, die Möglichkeit haben, etwaige Sachverhalte und Interessen, die eine objektive Begutachtung hindern können, anzugeben. Dies können finanzielle sowie akademische Interessen sein. Die Gutachter werden ersucht, Stellung zu nehmen und Interessen offen zu legen.''', is_inverted=True),
        Args('7b', 'Bestätigen Sie, dass Sie alle Informationen, die Sie im Rahmen dieser Begutachtung erhalten haben, vertraulich behandeln?'),
    ],
    'gcp_review': [
        Args( '1', 'Sind die Allgemeinen Informationen ausreichend und korrekt angegeben?'),
        Args( '2', 'Sind die Hintergrundinformationen ausreichend und korrekt angegeben?'),
        Args( '3', 'Ist das Studienziel und der Studienzweck detailliert beschrieben?'),
        Args( '4', 'Ist das Studiendesign ausreichend dargelegt? (Endpunkte, Studienphase, Bias-Vermeidung, Prüfpräparat, Labelling, Dauer, Beendigung, Accountability, Randomisierung, Source Daten)'),
        Args( '5', 'Sind Patientenauswahl und Austritts- bzw. Abbruchkriterien ausreichend definiert? (Ein-/Ausschluss, Abbruch, Datenerhebung, follow up, Ersatz)'),
        Args( '6', 'Ist die Behandlung der Studienteilnehmer, samt erlaubter/nicht erlaubter Medikation und Überprüfungsverfahren ausreichend definiert?'),
        Args( '7', 'Sind die Efficacy Parameter sowie Methoden, zeitliche Planung und Erfassung & Analyse d. Efficacy Parameter ausreichend definiert?'),
        Args( '8', 'Ist Safety und Safety Reporting Parameter ausreichend definiert, und adäquat?'),
        Args( '9', 'Sind die Angaben zur statistischen Datenerhebung, -Auswertung, -Methoden ausreichend und adäquat?'),
        Args('10', 'Ist die Qualitätskontrolle und Qualitätssicherung ausreichend beschrieben und sind diese Angaben adäquat?'),
        Args('11', 'Sind Angaben zu ethischen Aspekten vorhanden?'),
        Args('12', 'Sind Angaben zu Datenerhebung, Dokumentation und Verarbeitung ausreichend definiert und sind diese adäquat?'),
        Args('13', 'Sind Angaben zu Finanzierung und Versicherung ausreichend definiert und sind diese adäquat?'),
        Args('14', 'Sind Angaben zur Regelung bzgl Publikation ausreichend definiert?'),
        Args('15', 'Anhang, wenn zutreffend?'),
    ],
    'specialist_review': [
        Args('1', "Ist das Antragsformular korrekt und vollständig ausgefüllt?"),
        Args('2', "Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“?"),
        Args('3', "Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?"),
    ],
    'expedited_review': [
        Args('1', 'Kann das Projekt ohne ausführliche Diskussion in der Sitzung positiv beurteilt werden? (Ja=B1 oder B2)', requires_comment=True),    # XXX: dont change this number
        Args('2', "Ist das Antragsformular korrekt und vollständig ausgefüllt?", requires_comment=True),
        Args('3', "Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“ der MedUni Wien?", requires_comment=True),
        Args('4', "Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?"),
    ],
    'localec_review': [
        Args('1', 'Die Ethikkommission bestätigt als lokale Ethikkommission im Sinne des § 41b Abs. 5 AMG idF BGBl. I Nr. 23/2020 oder/und § 19 Abs. 4 Medizinproduktegesetz 2021 idgF die Eignung der Prüfer, seiner Mitarbeiter und die Angemessenheit der Einrichtungen in ihrem Zuständigkeitsbereich.'),     # XXX: dont change this number
    ],
}
