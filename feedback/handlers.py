from piston.handler import BaseHandler
from piston.doc import generate_doc
from feedback.models import Feedback
import datetime

class FeedbackHandler(BaseHandler):
    model = Feedback
    fields = ('id', 'feedbacktype', 'summary', 'description', 'origin', 'username', 'email', 'pub_date')
    allowed_methods = ('GET', 'PUT')
    
    def read(self, request, pk):
        return Feedback.objects.get(id=pk)
    
    def update(self, request, pk):
        obj = Feedback.objects.get(id=pk)
        for fieldname in "feedbacktype,summary,description,origin,username,email".split(","):
            setattr(obj, fieldname, request.PUT.get(fieldname))
            obj.save()
        return obj

class FeedbackCreate(BaseHandler):
    model = Feedback
    fields = ('id', 'feedbacktype', 'summary', 'description', 'origin', 'username', 'email', 'pub_date')

    allowed_methods = ("POST", "GET")
    def create(self, request):
        args = {"pub_date": datetime.datetime.now()}
        for fieldname in "feedbacktype,summary,description,origin,username,email".split(","):
            args[fieldname] = request.POST.get(fieldname)
        obj = Feedback(**args)
        obj.save()
        return obj

    def read(self, request):
        return Feedback.objects.all()

class FeedbackSearch(BaseHandler):
    model = Feedback
    fields = ('id', 'feedbacktype', 'summary', 'description', 'origin', 'username', 'email', 'pub_date')
    allowed_methods = ("GET", )
    def read(self, request, type, origin, offsetdesc):
        objs = Feedback.objects.order_by("id")
        if type != "all":
            objs = objs.filter(feedbacktype=type)
        if origin:
            print "applying origin limit", origin
            objs = objs.filter(origin=origin)
        offset = 0
        count = 20
        if offsetdesc:
            offsets = offsetdesc.split("/")
            if len(offsets) == 3:
                objs = objs.filter(origin=offsets[0])
                print "ORIGIN", offsets[0]
                offsets = offsets[1:]
            if len(offsets) == 2:
                count = int(offsets[1])
            if offsets[0] == "":
                pass
            elif offsets[0] == "last":
                offset = -count
            else:
                offset = int(offsets[0])
        print offset, count
        if offset >= 0:
            return objs.all()[offset:count]
        else:
            return list(objs.all())[offset:]

                

