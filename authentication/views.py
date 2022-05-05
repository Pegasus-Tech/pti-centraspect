from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_q.tasks import async_task

from authentication.forms import AdminCreateUserForm
from authentication.mixins import GroupRequiredMixin
from authentication.models import User, Account, Subscription, SubscriptionType
from centraspect import settings
from inspection_items import service as equipment_service


def registration_view(request):
    print(f'got request :: {request}')

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/register.html')
    
    if request.method == 'POST':
        data = request.POST
        sub = Subscription.objects.create(type=SubscriptionType.TRIAL)
        acct = Account.objects.create(name=data.get('company_name'),
                                      account_type=data.get('account_type'),
                                      subscription=sub)
        user = User.objects.create(
            account=acct,
            username=data.get('email').lower(),
            email=data.get('email').lower(),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'))
        user.set_password(data.get('password'))
        user.save()

        group = Group.objects.filter(name='Account Admin')
        if group.exists():
            user.groups.add(group.get())
            user.save()
        
        print(f'User :: [username: {user.username}, password: {user.password}]')
        
        authed_user = authenticate(request, username=user.username, password=request.POST.get('password'))
        print(f'Authed User :: {authed_user}')
        
        if authed_user is not None:
            login(request=request, user=authed_user)
            return redirect('dashboard')
           

def login_view(request):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/login.html')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
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


def forgot_password_view(request):
    if request.method == 'GET':
        return render(request, 'registration/password_reset_form.html', context={"form": PasswordResetForm})

    if request.method == 'POST':
        email = request.POST['email']
        if email is not None and email != '':
            user = User.objects.filter(email=email)
            if user.exists():
                async_task('task_worker.email_service.send_user_forgot_password_email', user.get())
                return render(request, 'registration/password_reset_done.html', context={"user_email": user.get().email})
            else:
                messages.error(request, f'No user with email {email} found. Please verify the entered email and try again.')
                return render(request, 'registration/password_reset_form.html', context={"form": PasswordResetForm})
        else:
            messages.error(request, f'Enter a valid email to send the instructions to.')
            return render(request, 'registration/password_reset_form.html', context={"form": PasswordResetForm})


@login_required
def user_detail_view(request, uuid):
    if request.method == 'GET':
        context = {}
        try:
            user = User.objects.get(uuid=uuid)
            context['user'] = user

            equipment = equipment_service.get_all_items_assigned_to_user(user=user)
            context['equipement'] = equipment

            return render(request, 'dashboard/users/user_details.html', context=context)

        except ValueError as e:
            print("Error getting equipment for user :: " + str(e))
            error = f"An unexpected error occurred trying to retrieve {user.get_full_name}'s assigned equipment.\n" \
                    f"Please contact your System Admin for support in resolving this issue."
            messages.error(request, error)
            return redirect('users:all')

        except Exception as e:
            print("Error getting user :: " + str(e))
            error = f'ERROR: No user found with UUID {uuid}'
            messages.error(request, error)
            return redirect('users:all')


@login_required
def edit_user_view(request, uuid):
    if request.method == 'POST':
        try:
            form = AdminCreateUserForm(request.POST or None)
            if form.is_valid():
                user = User.objects.get(uuid=uuid)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.username = form.cleaned_data['email']
                user.groups.clear()
                group = Group.objects.get(name=form.cleaned_data['group'])
                user.groups.add(group)
                user.save()
                messages.success(request, f'Success! {user.get_full_name} was successfully updated.')
                return redirect('users:all')
        except Exception as e:
            messages.error(request, "Error editing user. Please try again.")
            print(f'ERROR: error editing user with exception :: ', e)
            return redirect('users:all')


class AccountUsersListView(GroupRequiredMixin, LoginRequiredMixin, ListView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, ]
    template_name = 'dashboard/users/all_users.html'
    model = User
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.filter(account=self.request.user.account).filter(is_active=True)
        context["new_user_form"] = AdminCreateUserForm(None)
        context['groups'] = Group.objects.exclude(name='Superuser')
        return context


class AccountCreateUserView(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, ]
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
                user.groups.clear()
                group = Group.objects.get(name=user_form.cleaned_data['group'])
                user.groups.add(group)
                user.save()
                messages.success(request, f"Success! {user.get_full_name} was created.")
                async_task('task_worker.email_service.send_user_added_email', user, request.user.account)
            except Exception as e:
                print(f'Error Creating User :: {e}')
                if 'duplicate' in str(e):
                    messages.error(request, f'Error: A user with email \"{user.email}\" already exists.')
                else:
                    messages.error(request, f'Error: {e}')
            finally:
                return redirect("users:all")
        else:
            print(f'ERROR {user_form.errors}')
            messages.error(request, user_form.errors)
            return redirect("users:all")


class AccountUserDeactivateView(GroupRequiredMixin, LoginRequiredMixin, View):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, ]
    model = User
    
    def get(self, request, uuid):
        try:
            user = User.objects.get(uuid=uuid)
            if user is not None:
                user.is_active = False
                user.save()
                messages.warning(request, f'{user.get_full_name} has been deactivated.')
                return redirect('users:all')
        except Exception as e:
            print(f"Error Deactivating User :: {e}")
            messages.error(request, f"Error: No User Found For ID - {uuid}")
            return redirect("users:all")
