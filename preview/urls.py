from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('courses', views.all_courses, name='all_courses'),
    path('courses/math<int:course>', views.course_details, name='course_details'),
    path('courses/math<int:course>/<int:unit>', views.unit_details, name='unit_details'),
    path('create-checkout-session/<int:pk>', views.create_checkout_session, name='checkout_session'),
    path('checkout_success', views.checkout_success, name='checkout_success'),
    path('checkout_cancel', views.checkout_cancel, name='checkout_cancel'),
    path('<int:course>-<int:unit>-<int:concept>', views.concept_details, name='concept_details'),
    path('my-courses', views.my_courses, name='my_courses'),
    path('course-index', views.course_index, name='course_index'),
    path('webhook/stripe', views.stripe_webhook, name='stripe_webhook'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)