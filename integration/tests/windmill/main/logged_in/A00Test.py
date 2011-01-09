from windmill.authoring import WindmillTestClient

def TestnopTest():
    client = WindmillTestClient(__name__)
    client.waits.forElement(link=u'Logout', timeout=u'8000')
            
