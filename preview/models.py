from django.db import models
from users.models import Profile

class Concept(models.Model):
    concept_number = models.IntegerField(default=1)
    goal = models.CharField(max_length=200, blank=True, null=True)
    standard = models.CharField(max_length=200, blank=True, null=True)
    # Need to add a default html file to include if the concept is not found.
    concept_video = models.FileField(blank=True, null=True)

    def __str__(self):
        return f'{str(self.concept_number) + ": " + str(self.goal)}'

    class Meta:
        # Groups the concepts together by their unit, then orders by number
        ordering = ['concepts__unit_name', 'concept_number']
        verbose_name_plural = "  Concepts"

class Unit(models.Model):
    unit_name = models.CharField(max_length=200)
    concepts = models.ManyToManyField('Concept', related_name='concepts')
    unit_number = models.IntegerField(default=1)
    unit_blurb = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{str(self.unit_number) + ": " + self.unit_name}'

    class Meta:
        # Groups the units together by their course, then orders by number
        ordering = ['units__course_number', 'unit_number']
        verbose_name_plural = " Units"

class Course(models.Model):
    
    Math1 = 'Math 1'
    Math2 = 'Math 2'
    Math3 = 'Math 3'

    courses = [
        (Math1, 'Math 1 Preview'),
        (Math2, 'Math 2 Preview'),
        (Math3, 'Math 3 Preview'),
    ]
    
    course_name = models.CharField(
        max_length=200,
        choices=courses,
        default=Math2)

    units = models.ManyToManyField('Unit', related_name='units')
    course_number = models.IntegerField(default=2)
    
    price = models.IntegerField(default=199)
    price_id = models.CharField(max_length=100, null=True, blank=True)
    codename = models.CharField(max_length=100, null=True, blank=True)
    course_blurb = models.TextField(blank=True, null=True)
    course_initials = models.CharField(max_length=100, blank=True, null=True)
    course_color = models.CharField(max_length=100, blank=True, null=True)

    is_available_for_purchase = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.course_name}'

    class Meta:
        ordering = ['course_number']
        verbose_name_plural = "Courses"

def user_context(request):
    profile = request.user.profile
    course = Course.objects.get(course_number=profile.active_course)
    unit = course.units.get(unit_number=profile.active_unit)
    concept = unit.concepts.get(concept_number=profile.active_concept)
    
    # sets the values of prev and next concepts for pagination
    prev_concept = profile.active_concept - 1
    max_concept = unit.concepts.last().concept_number
    next_concept = None

    if profile.active_concept + 1 <= max_concept:
        next_concept = profile.active_concept + 1

    # generates the path to the html template for the active concept
    include_template = f'preview/concepts/{profile.active_course}.{profile.active_unit}.{profile.active_concept}.html'

    context = {
        'profile': profile,
        'course': course,
        'unit': unit,
        'concept': concept,
        'prev_concept': prev_concept,
        'next_concept': next_concept,
        'max_concept': max_concept,
        'include_template': include_template,
    }
    
    return context

def course_context(request):
    all_courses = Course.objects.all()
    can_purchase = all_courses.filter(is_available_for_purchase=True)
    excludes = []

    for temp_course in can_purchase:
        if request.user.has_perm(f'users.can_view_math{temp_course.course_number}'):
            excludes.append(temp_course.course_number)

    has_not_purchased = can_purchase.exclude(course_number__in=excludes)
    has_purchased = can_purchase.filter(course_number__in=excludes)

    context = {
        'all_courses': all_courses,
        'has_not_purchased': has_not_purchased,
        'has_purchased': has_purchased,
    }

    return context