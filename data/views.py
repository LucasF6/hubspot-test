from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from web.settings import HUBSPOT_AUTH_URL, HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI
from hubspot import HubSpot
from hubspot.crm.objects import SimplePublicObjectInputForCreate

client = HubSpot()

def home_with_error(request, error):
  context = {'auth_url': HUBSPOT_AUTH_URL}
  if error:
    context['error'] = error
  code = request.GET.get('code')
  if code:
    try:
      response = client.auth.oauth.tokens_api.create(
        grant_type='authorization_code',
        client_id=HUBSPOT_CLIENT_ID,
        client_secret=HUBSPOT_CLIENT_SECRET,
        redirect_uri=HUBSPOT_REDIRECT_URI,
        code=code)
      client.access_token = response.access_token
    except Exception as e:
      context['error'] = e
  if client.access_token:
    try:
      context['people'] = client.crm.contacts.get_all()
    except Exception as e:
      context['error'] = e
  return render(request, "data/home.html", context)

def home(request):
  return home_with_error(request, "")

def submit_contact(request):
  first_name = request.POST.get('first_name')
  last_name = request.POST.get('last_name')
  email = request.POST.get('email')
  if not (first_name and last_name and email and client.access_token):
    return home(request)
  try:
    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties={"email": email, "firstname": first_name, "lastname": last_name})
    client.crm.contacts.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)
  except Exception as e:
    return home_with_error(request, e)
  return HttpResponseRedirect(reverse('data:home'))

def delete_contact(request, person_id):
  if not client.access_token:
    return home(request)
  try:
    client.crm.contacts.basic_api.archive(contact_id=person_id)
  except Exception as e:
    return home_with_error(request, e)
  return HttpResponseRedirect(reverse('data:home'))
