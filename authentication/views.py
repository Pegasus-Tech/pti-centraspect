from typing import Any, Dict
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from authentication.forms import AdminCreateUserForm
from authentication.models import User, Account


def registration_view(request):
    print(f'got request :: {request}')

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/register.html')
    
    if request.method == 'POST':
        acct = Account.objects.create(name=request.POST.get('company_name'))
        user = User.objects.create(
            account=acct,
            username=request.POST.get('email'),
            email=request.POST.get('email'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'))
        user.set_password(request.POST.get('password'))
        user.save()
        
        print(f'User :: [username: {user.username}, password: {user.password}]')
        
        authed_user = authenticate(request, username=user.username, password=request.POST.get('password'))
        print(f'Authed User :: {authed_user}')
        
        if authed_user is not None:
            login(request=request, user=authed_user)
            return render(request=request, template_name='dashboard/index.html')
           

def login_view(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'registration/login.html', context)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request=request, username=username, password=password)
        
        if user is not None:
            print(f'Found user, logging in...')
            login(request=request, user=user)
            # this needs to redirect on login
            return redirect('dashboard')
        else:
            print(f'No user found with credentials u: {username} p: {password}')
            context['error'] = "Invalid username or password"
            return render(request, 'registration/login.html', context)
    
    else:
        response = render(request, '400.html')
        response.status_code = 400
        return response
    

def logout_view(request):
    logout(request)
    return redirect('login')
        

class AccountUsersListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/users/all_users.html'
    model = User
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.filter(account=self.request.user.account).filter(is_active=True)
        context["new_user_form"] = AdminCreateUserForm(None)
        return context
    
class AccountCreateUserView(LoginRequiredMixin, CreateView):
    model = User
    
    def post(self, request):
        print(f'REQUEST :: {request.POST}')
        user_form = AdminCreateUserForm(request.POST or None)
        if user_form.is_valid:
            user = user_form.save(commit=False)
            user.username = user.email
            user.account = request.user.account
            try:
                user.save()
                messages.success(request, f"Success! {user.get_full_name()} was created.")
            except Exception as e:
                print(f'Error Creating User :: {e}')
                messages.error(request, f'Error: {e}')
            finally:
                return redirect("users:all")
        else:
            print(f'ERROR {user_form.errors}')
            messages.error(request, user_form.errors)
            return redirect("users:all")
    
class AccountUserDeactivateView(LoginRequiredMixin, View):
    model = User
    
    def get(self, request, uuid):
        try:
            user = User.objects.get(uuid=uuid)
            if user is not None:
                user.is_active = False
                user.save()
                messages.warning(request, f'{user.get_full_name()} has been deactivated.')
                return redirect('users:all')
        except Exception as e:
            print(f"Error Deactivating User :: {e}")
            messages.error(request, f"Error: No User Found For ID - {uuid}")
            return redirect("users:all")