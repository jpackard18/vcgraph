from django.db import models
from django.utils import timezone
import pytz


class Error(models.Model):
    username = models.CharField(max_length=32)
    traceback = models.TextField()
    time_recorded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        est = pytz.timezone('US/Eastern')
        local_tr = self.time_recorded.astimezone(est)
        return "{} at {}".format(self.username, local_tr.strftime('%b. %d - %I:%M %p'))
