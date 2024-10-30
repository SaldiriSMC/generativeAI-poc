from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, PasswordUpdateForm


# Register view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            # Display all form errors in the error message
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# Login view
def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate the user
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('gen_ai_chat')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


# User profile update view
@login_required
def user_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('gen_ai_chat')
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'registration/user_update.html', {'form': form})


# Password update view
@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordUpdateForm(request.POST)
        if form.is_valid():
            user = request.user
            pre_password = form.cleaned_data['password']
            new_password = form.cleaned_data['password1']

            # Check if the old password is correct
            if not user.check_password(pre_password):
                messages.error(request, 'Your current password is incorrect.')
                return render(request, 'registration/update_password.html', {'form': form})

            # Set the new password and update the session
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')

            return redirect('gen_ai_chat')  # Redirect to a secure page after password change
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")

    else:
        form = PasswordUpdateForm()

    return render(request, 'registration/update_password.html', {'form': form})


def user_logout(request):
    return render(request, 'registration/logout.html')
