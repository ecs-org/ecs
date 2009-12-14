from django.db import models
from django.contrib import comments

class FeedbackComment(comments.Comment):
    """
    FeedbackComment extends Django's standard comment model, providing
    a "summary" and a "likecount" for each comment.
    """
    reference = models.CharField(max_length=64, null=True, blank=True,
        help_text="May be used by rendering interface to set additional "
                  "information")
    summary = models.CharField(max_length=80, null=False, blank=False)
    icon = models.CharField(max_length=32, null=True, blank=True,
        help_text="An icon associated with this post.  It could be used, "
                  "for example, to associate an emotion with a comment")
    likecount = models.IntegerField(default=0)
