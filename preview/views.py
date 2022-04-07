from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from preview.models import Course, Unit, Concept, user_context, course_context
from users.models import Profile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
import stripe
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import Permission, User
from threading import Thread

def index(request):
    context = {
        'all_courses': Course.objects.all(),
    }
    
    return render(request, 'preview/index.html', context)

@login_required
def concept_details(request, course, unit, concept):
    
    profile = request.user.profile

    if request.user.has_perm(f'users.can_view_math{course}'):
        profile.update_active(course, unit, concept)
    else:
        return redirect('/courses')

    return render(request, 'preview/concept_details.html', user_context(request))

def my_courses(request):
    return render(request, 'preview/my_courses.html', course_context(request))

@login_required
def course_index(request):
    profile = request.user.profile
    # Checks if user has any permissions - if they have purchased a course they will
    if len(request.user.get_user_permissions()) != 0:
        return render(request, 'preview/course_index.html', user_context(request))
    else:
        messages.info(request, "You have not purchased any courses yet.")
        return redirect('all_courses')

def all_courses(request):
    return render(request, 'preview/store/all_courses.html', course_context(request))

def course_details(request, course):
    course = Course.objects.filter(course_number=course).filter(is_available_for_purchase=True)[0]
    # find the number of units so course_details can correctly add comma
    number_of_units = course.units.last().unit_number
    units = course.units.all()

    context = {
        'course': course,
        'units': units,
        'number_of_units': number_of_units,
        }
        
    return render(request, 'preview/store/course_details.html', context)

def unit_details(request, course, unit):
    course = Course.objects.filter(course_number=course).filter(is_available_for_purchase=True)[0]
    unit = course.units.get(unit_number=unit)
    context = {
        'course': course,
        'unit': unit,
    }
    return render(request, 'preview/store/unit_details.html', context)

# Stripe Integration

stripe.api_key = settings.STRIPE_PRIVATE_KEY
endpoint_secret = settings.ENDPOINT_SECRET

@csrf_exempt
def create_checkout_session(request, pk):

    if not request.user.is_authenticated:
        messages.error(request, "Please sign in or create an account before continuing to checkout.")
        return redirect('/login/?next=/create-checkout-session/' + str(pk))

    course = Course.objects.get(pk=pk)
    price_id = course.price_id
    codename = course.codename

    YOUR_DOMAIN = 'https://mathbridgecourse.com'

    checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[
        {
            'price': price_id,
            'quantity': 1,
        },
    ],
    mode='payment',
    success_url=YOUR_DOMAIN + "/checkout_success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url=YOUR_DOMAIN + "/checkout_cancel?session_id={CHECKOUT_SESSION_ID}",
    metadata = {
        'user': request.user,
        'course': course,
        'course_pk': pk,
        'codename': codename,
        }
    )

    return redirect(checkout_session.url, code=303)

def checkout_success(request):
    session = stripe.checkout.Session.retrieve(request.GET['session_id'])

    context = {
        "session": session,
    }

    return render(request, 'preview/store/checkout_success.html', context)

def checkout_cancel(request):
    session = stripe.checkout.Session.retrieve(request.GET['session_id'])

    context = {
        "session": session,
    }

    return render(request, 'preview/store/checkout_cancel.html', context)

def add_course_to_account(session):
    metadata = session['metadata']
    username = metadata['user']
    codename = metadata['codename']
    user = User.objects.get(username=username)
    permission = Permission.objects.get(codename=codename)
    user.user_permissions.add(permission)
    user.user_permissions.save()

@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        background_thread = Thread(target=add_course_to_account, args=(session,))
        background_thread.start()
        
    return HttpResponse(status=200)
        
