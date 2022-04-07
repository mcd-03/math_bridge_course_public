from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_course = models.IntegerField(default=2)
    active_unit = models.IntegerField(default=1)
    active_concept = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user.username} Profile'
        
    def update_active(self, course, unit, concept):
        self.active_course = course
        self.active_unit = unit
        self.active_concept = concept
        self.save()

    class Meta:

        permissions = [
            ('can_view_math3', 'Can View Math 3'),
            ('can_view_math2', 'Can View Math 2'),
            ('can_view_math1', 'Can View Math 1'),
        ]