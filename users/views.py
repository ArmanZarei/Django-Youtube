from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from panel.utils import get_client_ip
from users.models import Profile
from .forms import UserRegisterForm, UserProfileRegisterationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        uform = UserRegisterForm(request.POST)
        pform = UserProfileRegisterationForm(request.POST)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()

            profile = pform.save(commit=False)
            profile.user = user
            if profile.role == Profile.Role.NORMAL:
                profile.is_approved = True
            profile.save()
            
            messages.success(request, f"Account created for {user.username}")
            return redirect('home')
    else:
        uform = UserRegisterForm()
        pform = UserProfileRegisterationForm()

    return render(request, 'users/auth/register.html', {"uform": uform, "pform": pform})


class CustomLogin(LoginView):
    def form_valid(self, form):
        if (form.get_user().profile.role == Profile.Role.ADMIN or form.get_user().profile.role == Profile.Role.OWNER) and get_client_ip(self.request) != settings.ALLOWED_VPN_IP:
            messages.error(self.request, "Permission denied. You have to use VPN to log in as an admin.")
            logout(self.request)
            return redirect('home')
        elif form.get_user().is_authenticated and form.get_user().profile.role == Profile.Role.ADMIN and not form.get_user().profile.is_approved:
            messages.error(self.request, "Permission denied. The owner of the website has not approved your registration yet. Please wait...")
            logout(self.request)
            return redirect('home')

        return super().form_valid(form)


class NewAdminRegistrationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    queryset = Profile.objects.filter(role=Profile.Role.ADMIN, is_approved=False).prefetch_related('user')
    context_object_name = 'profiles'
    template_name = 'users/new_admin_registrations.html'

    def test_func(self):
        return self.request.user.profile.role == Profile.Role.OWNER


@login_required
@user_passes_test(lambda user: user.profile.role == Profile.Role.OWNER)
def approve_admin_registration(request, user_pk):
    profile = Profile.objects.filter(user__pk=user_pk).get()
    if profile:
        profile.is_approved = True
        profile.save()
        messages.success(request, f"Admin \"{profile.user.username}\" approved")
    
    return redirect('new-admin-registrations')


class StrikedUsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    queryset = Profile.objects.filter(strike=True).prefetch_related('user')
    context_object_name = 'profiles'
    template_name = 'users/striked_users.html'

    def test_func(self):
        return self.request.user.profile.role == Profile.Role.ADMIN


@login_required
@user_passes_test(lambda user: user.profile.role == Profile.Role.ADMIN)
def remove_profile_strike(request, profile_pk):
    profile = Profile.objects.get(pk=profile_pk)
    if profile:
        profile.strike = False
        profile.save()
        messages.success(request, f"\"{profile.user.username}\"\'s strictions successfully removed")
    
    return redirect('striked-users-list')
