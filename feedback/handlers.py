from piston.handler import BaseHandler
from piston.doc import generate_doc
from feedback.models import Feedback
import datetime
from reversion.models import Version

class FeedbackHandler(BaseHandler):
    model = Feedback
    fields = ('id', 'feedbacktype', 'summary', 'description', 'origin', 'username', 'email', 'pub_date')
    allowed_methods = ('GET', 'PUT', "POST")
    
    def create(self, request, pk):
        obj = Feedback.objects.get(id=pk)
        if request.POST.get("metoo") != "false":
            obj.me_too_votes.add(request.user)
        else:
            obj.me_too_votes.remove(request.user)
        return "OK"
        
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
        for fieldname in "feedbacktype,summary,description,origin".split(","):
            args[fieldname] = request.POST.get(fieldname)
        obj = Feedback(**args)
        obj.save()
        return obj

    def read(self, request):
        return Feedback.objects.all()

class FeedbackSearch(BaseHandler):
    #model = Feedback
    #exclude = ()
    #fields = ('id', 'feedbacktype', 'summary', 'description', 'origin', 'qqqusername', 'email', 'pub_date')
    allowed_methods = ("GET", )

    @classmethod
    def username(dummy, self):
        version_list = Version.objects.get_for_object(self)
        print version_list[-1].revision.user
        return "XXX"

    def read(self, request, type, origin, offsetdesc):
        objs = Feedback.objects.order_by("id")
        if type != "all":
            objs = objs.filter(feedbacktype=type)
        if origin:
            objs = objs.filter(origin=origin)
        offset = 0
        count = 20
        if offsetdesc:
            offsets = offsetdesc.split("/")
            if len(offsets) == 3:
                objs = objs.filter(origin=offsets[0])
                offsets = offsets[1:]
            if len(offsets) == 2:
                count = int(offsets[1])
            if offsets[0] == "":
                pass
            elif offsets[0] == "last":
                offset = -count
            else:
                offset = int(offsets[0])
        print dir(self)
        if offset >= 0:
            data = list(objs.all()[offset:count])
        else:
            data = list(objs.all())[offset:]
        result = []
        for item in data:
            ditem = {}
            for k in ('id', 'feedbacktype', 'summary', 'description', 'origin', 'pub_date'):
                ditem[k] = getattr(item, k, None)
                ditem["metoo"] = 0
                try:
                    user = list(Version.objects.get_for_object(item))[-1].revision.user
                    ditem["username"] = user.username
                    ditem["email"] = user.email
                    if user == request.user:
                        ditem["metoo"] = 2
                except:
                    import sys
                    print sys.exc_info()
                me_too_users = list(item.me_too_votes.all())
                if request.user in me_too_users:
                    ditem["metoo"] = 1
            result.append(ditem)
        return result

                

