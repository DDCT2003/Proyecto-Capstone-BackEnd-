from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    required_skills = models.JSONField(default=list)  # ["React","Django"]
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    priority = models.IntegerField(default=3)  # 1=alta ... 5=baja

    def __str__(self):
        return self.title
