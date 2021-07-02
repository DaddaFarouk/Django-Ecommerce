from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():                                        # fetch values from form
            first_name        = form.cleaned_data['first_name']
            last_name         = form.cleaned_data['last_name']
            email             = form.cleaned_data['email']
            phone_number      = form.cleaned_data['phone_number']
            password          = form.cleaned_data['password']      # the confirm_password will be validated in the form level
            username          = email.split("@")[0]
            user              = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number                       # because the create_user function doesn't take the phone_number as a prop
            user.save()

            # USER ACTIVATION
            current_site      = get_current_site(request)
            mail_subject      = 'Please activate your account'
            message           = render_to_string('accounts/account_verification_email.html',{
                'user'   : user,
                'domain' : current_site,
                'uid'    : urlsafe_base64_encode(force_bytes(user.pk)), # encoding the user's id so nobody can see the PrimaryKey
                'token'  : default_token_generator.make_token(user),     # create token for the user
            })
            to_email          = email
            send_email        = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            #messages.success(request, 'Thank you for registering. We have sent you a verification email to [ email ]')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()


    
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request,'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')



    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:

        uid  = urlsafe_base64_decode(uidb64).decode() # decode the uidb64
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): # check the user's token
       
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is Activated!')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')




@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) # case sensitive

            # Reset password email
            current_site      = get_current_site(request)
            mail_subject      = 'Reset Your Password'
            message           = render_to_string('accounts/reset_password_email.html',{
                'user'   : user,
                'domain' : current_site,
                'uid'    : urlsafe_base64_encode(force_bytes(user.pk)), # encoding the user's id so nobody can see the PrimaryKey
                'token'  : default_token_generator.make_token(user),     # create token for the user
            })
            to_email          = email
            send_email        = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email adress.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:

        uid  = urlsafe_base64_decode(uidb64).decode() # decode the uidb64
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): # check the user's token
        request.session['uid'] = uid                 # get user's uid to access it later
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    
    else:
        messages.error(request, 'This link expired')
        return redirect('login')



def resetPassword(request):
    if request.method =='POST':
        password         = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid  = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)  # to save the hashed password 
            user.save()
            messages.success(request, 'Password successfully reseted')
            return redirect('login')
        
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetPassword')

    else:
        return render(request, 'accounts/resetPassword.html')