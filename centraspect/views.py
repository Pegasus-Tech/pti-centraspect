from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import csrf_exempt
from django_q.tasks import async_task

from . import messages as centra_messages


class LandingPage(TemplateView):
    template_name = 'landing.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'


class TermsAndConditionsView(TemplateView):
    template_name = 'terms_and_conditions.html'


class SupportView(View):
    template_name = 'support.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name)

    def post(self, request, **kwargs):
        form = self.request.POST
        print(f'got support form {form}')

        if form['full_name'] is None or form['full_name'] == '':
            messages.error(request, 'You must provide your name with your support request.')
            return redirect('support')

        if form['email'] is None or form['email'] == '':
            messages.error(request, 'You must provide an email to respond to with your support request.')
            return redirect('support')

        if form['support_ticket_body'] is None or form['support_ticket_body'] == '':
            messages.error(request, 'A support ticket cannot be sent with an empty details section. '
                                    'Please provide details and resend.')
            return redirect('support')

        async_task('task_worker.email_service.send_support_request_email', form)
        messages.success(request, 'Thank you! We received your request and will respond via email soon!')
        return redirect('support')

@csrf_exempt
def return_invalid_token_response(request, *args, **kwargs):
    error_message = kwargs.pop('error_message') or None
    if error_message is None:
        error_message = centra_messages.GENERIC_ERROR

    return JsonResponse(status=401, data={"Token Error": error_message})


@csrf_exempt
def return_token_expired_response(request, *args, **kwargs):
    error_message = kwargs.pop('error_message') or None
    if error_message is None:
        error_message = centra_messages.AUTH_TOKEN_EXPIRED_ERROR

    return JsonResponse(status=401, data={"Token Expired": error_message})


