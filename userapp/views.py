from django.contrib import auth
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import render, redirect
from .models import CustomUser, UserProfile
from django.contrib.auth import get_user_model
from pyotp import TOTP
from django.core.mail import send_mail
from .models import OTPModel
from django.utils import timezone

User = get_user_model()

def index(request):
    return render(request, "index.html")


# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('pass')

#         if email and password:
#             user = authenticate(request, email=email, password=password)
#             print("Authenticated user:", user)  # Print the user for debugging
#             if user is not None:
#                 auth_login(request, user)
#                 return redirect('http://127.0.0.1:8000/')
#             else:
#                 error_message = "Invalid login credentials."
#                 return render(request, 'login.html', {'error_message': error_message})
#         else:
#             error_message = "Please fill out all fields."
#             return render(request, 'login.html', {'error_message': error_message})

#     return render(request, 'login.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')

        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role
                return redirect('/')
            else:
                error_message = "Invalid login credentials."
                return render(request, 'login.html', {'error_message': error_message})
        else:
            error_message = "Please fill out all fields."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def admin_login(request):
    error_message = None  # Initialize error message variable

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')

        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.role == 'admin':
                    auth_login(request, user)
                    request.session['user_email'] = user.email
                    request.session['user_role'] = user.role
                    return redirect('/')
                else:
                    error_message = "This user is not registered as admin."
            else:
                error_message = "Invalid login credentials."
        else:
            error_message = "Please fill out all fields."

    return render(request, 'admin_login.html', {'error_message': error_message})

def register(request):
    error_message = ''
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('sname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        role = User.STOWNER

        if first_name and last_name and email and phone and role and password:
            if User.objects.filter(email=email,phone=phone).exists():
                error_message = "Email is already registered."
            else:
                # Create the user but don't activate it yet
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    role=role
                )
                user.set_password(password)
                user.is_active = False
                user.save()
                
                # Generate and send OTP
                otp = TOTP('JBSWY3DPEHPK3PXP').now()
                otp_record = OTPModel.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                send_otp_email(user.email, otp)
                
                # Redirect to OTP verification page with user_id
                return redirect('verify_otp', user_id=user.id)

    return render(request, 'register.html', {'error_message': error_message, 'role': CustomUser.STOWNER})

def registerWK(request):
    error_message = ''
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('sname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        role = User.WORKER

        if first_name and last_name and email and phone and role and password:
            if User.objects.filter(email=email,phone=phone).exists():
                error_message = "Email is already registered."
            else:
                # Create the user but don't activate it yet
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    role=role
                )
                user.set_password(password)
                user.is_active = False
                user.save()
                
                # Generate and send OTP
                otp = TOTP('JBSWY3DPEHPK3PXP').now()
                otp_record = OTPModel.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=timezone.now() + timezone.timedelta(minutes=10)
                )
                send_otp_email(user.email, otp)
                
                # Redirect to OTP verification page with user_id
                return redirect('verify_otp', user_id=user.id)

    return render(request, 'register_worker.html', {'error_message': error_message, 'role': CustomUser.WORKER})


def verify_otp(request, user_id=None):
    user = User.objects.get(id=user_id)
    otp_record = OTPModel.objects.filter(user=user, expires_at__gt=timezone.now()).first()

    if not otp_record:
        return redirect('registration')  # Redirect if OTP is expired or not found

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == otp_record.otp:
            otp_record.delete()  # Delete OTP record after successful verification
            user.is_active = True
            user.save()
            return redirect('login')  # Redirect to login page

    return render(request, 'verify_otp.html')



def send_otp_email(to_email, otp):
    subject = 'Your OTP for Account Verification'
    message = f'Your OTP is: {otp}'
    from_email = 'info.plugspot@gmail.com'  # Replace with your email
    send_mail(subject, message, from_email, [to_email])
    

def vhowner(request):
    error_message = ""
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('sname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        role = User.VHOWNER
        print(first_name, last_name, phone, password, role)
        if first_name and last_name and email and phone and role and password:
            if User.objects.filter(email=email,phone=phone).exists():
                error_message = "Email is already registered."
                return render(request, 'register_vh.html', {'error_message': error_message})

            else:

                user = User(first_name=first_name, last_name=last_name,
                            phone=phone, email=email, role=role)
                user.set_password(password)
                user.save()
                user_profile = UserProfile(user=user)
                user_profile.save()
                otp = TOTP('JBSWY3DPEHPK3PXP').now()
                otp_record = OTPModel.objects.create(user=user, otp=otp, expires_at=timezone.now() + timezone.timedelta(minutes=10))
                send_otp_email(user.email, otp)
                return redirect('verify_otp', user_id=user.id)
                # return render(request, 'login.html')

    return render(request, 'register_vh.html', {'role': CustomUser.VHOWNER})


def logout(request):
    auth.logout(request)
    return redirect('index')


def profile(request):
    user_profile1 = request.user
    userid = user_profile1.id
    
    print(user_profile1)
    check=UserProfile.objects.filter(user_id=userid).exists()
    if check:
        user_profile = UserProfile.objects.get(user_id=userid)
    else:
        user_profile=None

    if request.method == 'POST':
        # Update user fields
        if check==True:
            user_profile.first_name = request.POST.get('first_name')
            user_profile.last_name = request.POST.get('last_name')
            user_profile.phone_no = request.POST.get('phone_no')
            user_profile.save()

             # Update user profile fields
            user_profile.country = request.POST.get('country')
            print(user_profile.country)
            user_profile.state = request.POST.get('state')
            user_profile.city = request.POST.get('city')
            user_profile.district = request.POST.get('district')
            user_profile.aphone_no = request.POST.get('aphone_no')
            user_profile.phone_no = request.POST.get('phone_no')
            user_profile.addressline1 = request.POST.get('addressline1')
            user_profile.addressline2 = request.POST.get('addressline2')
            user_profile.pin_code = request.POST.get('pin_code')
            user_profile.save()
        else:
            user=UserProfile(
                phone_no = request.POST.get('phone_no'),

             # Update user profile fields
                country = request.POST.get('country'),
                state = request.POST.get('state'),
                city = request.POST.get('city'),
                district = request.POST.get('district'),
                aphone_no = request.POST.get('aphone_no'),
                addressline1 = request.POST.get('addressline1'),
                addressline2 = request.POST.get('addressline2'),
                pin_code = request.POST.get('pin_code'),
                user_id=userid
            )
            user.save()

        return redirect('index')
    context = {
        'user': user_profile1,
        'user_profile': user_profile
    }
    return render(request, 'profile.html', context)

