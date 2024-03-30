from decimal import Decimal
from io import BytesIO
from django.urls import reverse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

from make_service.models import service_booking
from .form import SubscriptionForm
from django.shortcuts import render, redirect
from .models import station, booknow, CustomUser,Subscription
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import On_payment
from django.db.models import Q
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.core.mail import send_mail
from django.template.loader import render_to_string
import pytz
from django.utils import timezone

# Create your views here.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def predict(request):
    return render(request,'home.html')

@login_required(login_url='http://127.0.0.1:8000/login/')
def booking(request):
    expired()   
    stdata = station.objects.filter(hidden=False)

    return render(request, "booking.html", {'stdata': stdata})

def contact(request):
    return render(request,'contact.html')

def subscription(request):
    subscriptions = Subscription.objects.all()
    # Process the features for each subscription
    for sub in subscriptions:
        sub.features = sub.features.split(',')

    context = {
        'user': request.user,
        'subscriptions': subscriptions,
    }
    return render(request, "pricing.html", context=context)


def bookstation(request, station_id):
    user = request.user
    user_id = user.id
    error_message = ''

    data = station.objects.filter(id=station_id)
    data=data[0]
    if data.available is None:
        data.available = data.maxslot

    available_slot_numbers = data.maxslot
    
    # Generate a list of available slot numbers
    if available_slot_numbers is None:
        available_slot_numbers = list(range(1, data.maxslot + 1))


    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        slotnumber = request.POST.get('your_slot')

        # Check if the slot is already booked within the specified time range
        existing_booking = booknow.objects.filter(
                date=date,
                status=True,
                station_id_id=station_id,
                slotnumber=slotnumber,
                start_time__lte=start_time,  # Check if the existing start time is less than or equal to the new start time
                end_time__gte=end_time,      # Check if the existing end time is greater than or equal to the new end time
            ).first()

        if existing_booking:
            error_message = "Slot already booked"
        else:
                
            post = booknow(
                name=user,  # Assuming 'name' and 'email' are ForeignKey fields in 'booknow'
                email=user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                photo=data.photo,
                slotnumber=slotnumber,
                stname=data.stname,
                place=data.place,
                price=data.price,
                ownername=data.ownername,
                station_id_id=station_id,
                status = False
            )
            

            # No need to decrement data.available here
            # data.available -= 1
            # data.save()
            post.save()
            # history_entry.save()

            
            latest_booking=post.id
            # history_id = history_entry.id
            print("latest_booking"+str(latest_booking))
            return redirect('http://127.0.0.1:8000/bookings/calculate_cost/'+str(latest_booking)+'/')

   
    available_slot_numbers = [num for num in range(1, data.maxslot + 1)]

    return render(request, "booknow.html", {'available_slot_numbers': available_slot_numbers, 'error_message': error_message})



def expired():
    # Check for expired bookings and make slots available
    now = datetime.now()
    expired_bookings = booknow.objects.filter(
        Q(date__lt=now.date()) | (Q(date=now.date()) & Q(end_time__lt=now.time())) & Q(del_status=False)
    )
    for booking in expired_bookings:
        booking.del_status = True 
        booking.save()


def calculate_cost(request, stid2):
    data = booknow.objects.filter(id=stid2)
    

    # You may need to iterate through data if there are multiple records
    for item in data:
        start_time = item.start_time.strftime('%H:%M:%S')  # Convert to HH:MM:SS format
        end_time = item.end_time.strftime('%H:%M:%S')      # Convert to HH:MM:SS format

        charging_rate = 12  # Charging rate in kW
        cost_per_unit = 15  # Cost per unit in rupees/kWh

        # Calculate the charging duration in hours
        start_datetime = datetime.strptime(start_time, '%H:%M:%S')
        end_datetime = datetime.strptime(end_time, '%H:%M:%S')

        # Calculate the time difference (duration)
        charging_duration = end_datetime - start_datetime

        # Convert the duration to hours
        charging_duration_hours = charging_duration.total_seconds() / 3600

        # Calculate the total energy consumed during the charging session in kWh
        energy_consumed = charging_rate * charging_duration_hours

        # Calculate the total cost for the charging session in rupees
        total_cost = energy_consumed * cost_per_unit
        total_cost=int(total_cost)

        if request.method=='POST':
            return redirect('http://127.0.0.1:8000/bookings/payment/'+str(total_cost)+'/')

        # Render the result in the template
        return render(request, 'payment1.html', {'total_cost': total_cost, 'data': data})
    


def payment1(request, booking_id=None, cost=None, sub_id=None, total_cost =None, service_id= None):
    currency = 'INR'
    amount = None  # Initialize amount
    print(service_id)

    if booking_id and cost:
        # Handle booking payment
        amount = cost * 100  # Convert cost to paise
        sub_id = None  # Set sub_id to None since it's not used for bookings
        booking = booknow.objects.get(pk=booking_id)
        date=datetime.now()
        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency=currency,
            payment_capture='0'
        ))

        # Order ID of the newly created order
        razorpay_order_id = razorpay_order['id']
        print('booking_pay')
        callback_url = reverse('paymenthandler_booking', args=[booking_id])  # You can adjust the callback URL as needed

        payment = On_payment.objects.create(
            user=request.user,
            amount=amount / 100,  # Convert amount back to Decimal
            payment_id='',
            booking=booking,  # Set booking_id based on conditions
            order=razorpay_order_id,
            status=True  # Use a boolean value here
        )

        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency,
            'callback_url': callback_url,
        }

        return render(request, 'payment.html', context=context)

    elif sub_id:
        # Handle subscription payment
        sub_type = Subscription.objects.get(pk=sub_id)
        amount = int(sub_type.price * 100)  # Convert price to paise

        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency=currency,
            payment_capture='0'
        ))

        # Order ID of the newly created order
        razorpay_order_id = razorpay_order['id']
        print('sub_payment')
        callback_url = reverse('paymenthandler_subscription', args=[sub_id])  # You can adjust the callback URL as needed

        payment = On_payment.objects.create(
            user=request.user,
            amount=amount / 100,  # Convert amount back to Decimal
            payment_id='',
            subscribe=sub_type,  # Set subscribe_id based on conditions
            order=razorpay_order_id,
        )

        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency,
            'callback_url': callback_url,
        }

        return render(request, 'payment.html', context=context)
    
    elif service_id and total_cost:
        total_cost=float(total_cost)
        total_cost=int(total_cost)
        # Handle booking payment
        amount = total_cost * 100  # Convert cost to paise
        sub_id = None  # Set sub_id to None since it's not used for bookings
        booking_id = None
        additional_service = service_booking.objects.get(pk=service_id)
        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency=currency,
            payment_capture='0'
        ))

        # Order ID of the newly created order
        razorpay_order_id = razorpay_order['id']
        print("service_payment")
        callback_url = reverse('paymenthandler_service', args=[service_id])  # You can adjust the callback URL as needed

        payment = On_payment.objects.create(
            user=request.user,
            amount=amount / 100,  # Convert amount back to Decimal
            payment_id='',
            additional_service=additional_service,  # Set booking_id based on conditions
            order=razorpay_order_id,
            status=True  # Use a boolean value here
            
        )
        payment.save()

        context = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency,
            'callback_url': callback_url,
        }

        return render(request, 'payment.html', context=context)

    else:
    
        # Handle invalid URL or other cases as needed
        return HttpResponse("Invalid URL")

@csrf_exempt
def paymenthandler(request, service_id=None, booking_id=None, sub_id=None):
    print(booking_id,service_id)
    
    # Only accept POST requests.
    if request.method == "POST":
        # Get the required parameters from the POST request.
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        # Verify the payment signature.
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        print(service_id)
        payment = On_payment.objects.get(order=razorpay_order_id)
        payment.status= True
        # Capture the payment.
        amount = int(payment.amount * 100)  # Convert Decimal to paise
        razorpay_client.payment.capture(payment_id, amount)

        # Update the order with payment ID and change status to "Successful."
        payment.payment_id = payment_id
        payment.status = True
        payment.save()

        if booking_id:
            try:
                # Update the Reservation status to True.
                booking = booknow.objects.get(id=booking_id)
                booking.status = True
                booking.save()
                
                send_welcome_email(payment.user.username, amount, payment.user.email, booking)
            except booknow.DoesNotExist:
                # Handle the case where the booking with the given ID doesn't exist.
                pass

        if service_id:
            print("if")
            try:
                print("try")
                # Update the Reservation status to True.
                booking = service_booking.objects.get(id=service_id)
                booking.payment_done = True  # Update payment_done to True
                booking.save()
                # Redirect to the feedback page with ser_id parameter
                station_id=booking.package.service.service.id
                return redirect(reverse('feedback_page', kwargs={'ser_id': station_id}))
                
            except service_booking.DoesNotExist:
                # Handle the case where the booking with the given ID doesn't exist.
                pass

        # Render the success page on successful capture of payment.
        return render(request, 'index.html')

    else:
        return HttpResponseBadRequest()


def send_welcome_email(username, amount, email, booking):
    amount /= 100  # Convert amount back to the original format (from paise to the original currency)
    subject = 'Welcome to Plugspot'
    message = f"Hello {email},\n\n"
    message += f"Welcome to Plugspot, your platform for finding your nearest EV charging station. We are excited to have you join us!\n\n"
    
    if booking:
        message += f"You have booked a station at {booking.stname}, {booking.place} with slot number {booking.slotnumber}.\n\n"
    
    message += f"The total amount paid is {amount}.\n\n"

    message += "Please feel free to contact the station owner for more information.\n\n"
    message += "Thank you for choosing Plugspot. We wish you the best in your property search!\n\n"
    message += "Warm regards,\nThe Plugspot Team\n\n"
    
    from_email = 'info.plugspot@gmail.com'  # Replace with your actual email
    recipient_list = [email]  # Use the provided email
    
    send_mail(subject, message, from_email, recipient_list)


# def send_welcome_email_service(username, amount, email, service_booking):
#     service_name = service_booking.service_name  # Accessing service_name attribute directly
#     location = service_booking.location
#     service_date = service_booking.date
#     service_time = service_booking.time

#     amount /= 100  # Convert amount back to the original format (from paise to the original currency)
#     subject = 'Welcome to Plugspot'
#     message = f"Hello {username},\n\n"
#     message += f"Welcome to Plugspot, your platform for finding the nearest EV service stations. We're thrilled to have you join us!\n\n"
    
#     message += f"You have successfully booked a service at {service_name}, located at {location}.\n\n"
#     message += f"Your booking details:\n"
#     message += f"Service Name: {service_name}\n"
#     message += f"Location: {location}\n"
#     message += f"Service Date: {service_date}\n"
#     message += f"Service Time: {service_time}\n"
#     # Add more relevant booking details as needed
    
#     message += f"The total amount paid is {amount}.\n\n"
#     message += "Please feel free to contact the service station owner for more information.\n\n"
#     message += "Thank you for choosing Plugspot. We wish you a pleasant experience!\n\n"
#     message += "Warm regards,\nThe Plugspot Team\n\n"
    
#     from_email = 'info.plugspot@gmail.com'  # Replace with your actual email
#     recipient_list = [email]  # Use the provided email
    
#     send_mail(subject, message, from_email, recipient_list)


@login_required
def addstation(request):
    user = request.user
    userid = user.id
    stnumber = range(1, 16)
    if request.method == 'POST':
        stname = request.POST.get('stname')
        ownername = request.POST.get('ownername')
        place = request.POST.get('loc')
        contact = request.POST.get('number')
        photo = request.FILES.get('photo')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        maxslot = request.POST.get('max_slot')
        available = maxslot
        date=datetime.now()
        description = request.POST.get('desc')
        price = request.POST.get('price')

        post = station(
            stname=stname,
            place=place,
            photo=photo,
            ownername=ownername,
            latitude=latitude,
            contact=contact,
            longitude=longitude,
            maxslot=maxslot,
            date=date,
            available = available,
            description=description,
            price=price,
            user_id=userid
        )
        post.save()

        return redirect('subscription')
    return render(request, "addstation.html", {'stnumber': stnumber})

def allbooking(request):
    expired()
    current_user = request.user
    owned_stations = station.objects.filter(user=current_user)
    stdata = booknow.objects.filter(station_id__in=owned_stations,status=True,del_status=False)
    return render(request, "allbooking.html", {'stdata': stdata})


def mystation(request):
    expired()
    user_id = request.user.id
    mystation = station.objects.filter(user_id=user_id, hidden=False)
    return render(request, "mystation.html", {'mystation': mystation})


def mybookings(request, station_id=None):
    expired()
    user_id = request.user.id
    mybookings = booknow.objects.filter(email_id=user_id,status=True,del_status= False)


    contact = None  # Initialize contact as None

    if mybookings:
        station_instance = station.objects.filter(
            id=mybookings[0].station_id.pk).first()
        if station_instance:
            contact = station_instance.contact  # Assign contact if station_instance exists

    return render(request, "mybooking.html", {'mybookings': mybookings, 'contact': contact})

def delete_booking(request, stid2):

    item_to_delete = booknow.objects.get(id=stid2)

    if request.method == 'POST' and item_to_delete:
        item_to_delete.status=False

        item_to_delete.save()

        return redirect('mybookings')
    
    return render(request, 'mybooking.html', {'item_to_delete': item_to_delete})


def dashboard(request):
    expired()
    data = CustomUser.objects.all()
    total_user = CustomUser.objects.filter(is_active=True).count()
    total_book = booknow.objects.filter(del_status=False).count()
    total_complete=booknow.objects.count()
    station_count = station.objects.count()
    payment_count = On_payment.objects.filter(status=True).count()


    context = {
        'data': data,
        'total_user': total_user,
        'user_book': total_book,
        'total_complete':total_complete ,
        'station_count': station_count,
        'payment_count':payment_count,

    }
    return render(request, "user_dash.html", context)


def station_dash(request):
    stdata = station.objects.all()
    data = CustomUser.objects.all()
    total_user = CustomUser.objects.filter(is_active=True).count()
    total_book = booknow.objects.filter(del_status=False).count()
    total_complete=booknow.objects.count()
    station_count = station.objects.count()
    payment_count = On_payment.objects.filter(status=True).count()


    context = {
        'stdata':stdata,
        'data': data,
        'total_user': total_user,
        'user_book': total_book,
        'total_complete':total_complete ,
        'station_count': station_count,
        'payment_count':payment_count,
    }
    # 'total_payments': total_payments,
    return render(request, "station_dash.html", context)

def booking_dash(request):
    stdata = booknow.objects.filter(del_status=False)
    data=booknow.objects.all()
    data = CustomUser.objects.all()
    total_user = CustomUser.objects.filter(is_active=True).count()
    total_book = booknow.objects.filter(del_status=False).count()
    total_complete=booknow.objects.count()
    station_count = station.objects.count()
    payment_count = On_payment.objects.filter(status=True).count()

    context = {
        'stdata':stdata,
        'data': data,
        'total_user': total_user,
        'user_book': total_book,
        'total_complete':total_complete ,
        'station_count': station_count,
        'payment_count':payment_count,
      
    }
    # 'total_payments': total_payments,
    return render(request, "bookingdash.html", context)


def update(request, stid2):
    stid = station.objects.get(id=stid2)
    stid1 = station.objects.filter(id=stid2)
    
    stnumber = range(1, 16)
    message =''
    if request.method == 'POST':
        stid.stname = request.POST.get('stname')
        stid.ownername = request.POST.get('ownername')
        stid.place = request.POST.get('loc')
        stid.latitude = request.POST.get('lat')
        stid.longitude = request.POST.get('long') 
        new_max_slot = int(request.POST.get('max_slot'))
        if new_max_slot >= stid.available:
            stid.maxslot = new_max_slot
            # message = "invalid update"
        stid.description = request.POST.get('desc')
        stid.price = request.POST.get('price')

        if 'photo' in request.FILES:
            stid.photo = request.FILES['photo']

        stid.save()
        return redirect("mystation")

    return render(request, 'updatestation.html', {'station': stid1, 'stnumber': stnumber,'message':message})

def closed(request):
    stdata = station.objects.filter(hidden=True)
    return render(request, 'shutdown.html', {'stdata': stdata})

def show(request, stid2):
    queryset = station.objects.get(id=stid2)
    if request.method == 'POST':
        queryset.hidden = False
        queryset.save()
        return redirect('mystation')
    return render(request, 'mystation.html')


def hide(request, stid2):
    station_to_hide = station.objects.get(id=stid2)
    error_message =''
    if request.method == 'POST':
        # Check if there are any bookings for the current station
        existing_bookings = booknow.objects.filter(station_id=station_to_hide.id)
        
        station_to_hide.hidden = True
        station_to_hide.save()    
        return redirect('mystation')    
    return render(request, 'mystation.html',{'existing_bookings':existing_bookings})

def delete_items(request, stid2):
    queryset = station.objects.get(id=stid2)
    if request.method == 'POST':
        queryset.hidden = True
        queryset.save()
        return redirect('mystation')
    return render(request, 'mystation.html')

def delete_adm_station(request, stid2):
    queryset = station.objects.get(id=stid2)
    queryset.hidden=True
    queryset.save()
    return redirect('station_dash')

def delete_adm_user(request, stid2):
    queryset = CustomUser.objects.get(id=stid2)
    queryset.is_active = False
    queryset.save()
    return redirect('dashboard')

def delete_adm_book(request, stid2):
    print(stid2)
    queryset = booknow.objects.get(id=stid2)
    queryset.del_status = True
    queryset.save()
    return redirect('booking_dash')

def print_as_pdf(request, stid2):

    data = booknow.objects.filter(id=stid2)
    cost = On_payment.objects.get(booking_id=stid2)
    cost=cost.amount
    cost=cost
    
    total_cost=int(cost)
    print(cost)
    template_path = 'template\printpdf.html'  # Update with the actual path to your HTML template.

    # Context data to pass to the template
    context = {'data': data,'total_cost': total_cost}

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{stid2}.pdf"'

    # Render the HTML template to PDF
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
        rendered_html = render(request, 'printpdf.html', context)

        # Create a PDF using pisa
        pisa_status = pisa.CreatePDF(
            rendered_html.content,
            dest=response,
            link_callback=None  # Optional: Handle external links
        )
    return response


def check_bookings(request):
    user_id = request.user.id
    
    # Use Django's timezone to get the current date and time
    current_datetime_utc = timezone.now()

    # Convert to IST (Indian Standard Time)
    ist = pytz.timezone('Asia/Kolkata')
    current_datetime_ist = current_datetime_utc.astimezone(ist)
    print(current_datetime_ist)
    # Query BookingHistory to get all ended bookings for the logged-in user
    ended_bookings = booknow.objects.filter(email_id=user_id,del_status=True).order_by('-end_time')
    # amount = On_payment.objects.get()
    context = {
         'ended_bookings': ended_bookings,
    }
    
    return render(request, 'bookhistory.html', context)

def subscription_view(request):
    # Get all subscription plans
    subscriptions = Subscription.objects.all()

    # Get the user's subscribed plans (if any)
    user_subscriptions = On_payment.objects.filter(user=request.user, subscribe__isnull=True)
    
    # Create a set of subscription IDs that the user has subscribed to
    subscribed_plan_ids = set(subscribe.id for subscribe in user_subscriptions)
    unpaid_payments = On_payment.objects.filter(status=False)
    context = {
        'unpaid_payments': unpaid_payments,
        'subscriptions': subscriptions,
        'subscribed_plan_ids': subscribed_plan_ids,
    }

    return render(request, 'pricing.html', context)
    
def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            sub_type = form.cleaned_data['sub_type']
            price = form.cleaned_data['price']
            validity = form.cleaned_data['validity']
            features_list = form.cleaned_data['features'].split(',')
            features_csv = ','.join(features_list)
            

            if Subscription.objects.filter(
                sub_type=sub_type,
                price=price,
                validity=validity,
                features=features_csv
            ).exists():
                
                form.add_error(None, "A subscription with the same data already exists.")
            else:
               
                subscription = form.save(commit=False)
                subscription.features = features_csv
                subscription.save()
                return redirect('dashboard')
    else:
        form = SubscriptionForm()
    
    return render(request, 'add_subscription.html', {'form': form})

 # For user to know his booking
def booking_receipt(request):
    user_id = request.user.id
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Query the purchase history for records within the specified date range
        booking_history = booknow.objects.filter(
            email_id=user_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
  
        context = {
            'booking_history': booking_history,
            'start_date': start_date,
            'end_date': end_date,
            # 'total_price': total_price,  # Pass the total_price to the template
        }    


        # Render the receipt template to HTML
        template_name = 'book_receipt.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'

        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)
        
        if not pdf.err:
            response.write(buffer.getvalue())
            return response
        response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'

    # Render the HTML template to PDF
    with open('user/receipt.html', 'r') as template_file:
        template_content = template_file.read()
        rendered_html = render(request, 'book_receipt.html', context)

        # Create a PDF using pisa
        pisa_status = pisa.CreatePDF(
            rendered_html.content,
            dest=response,
            link_callback=None  # Optional: Handle external links
        )
    return response


 # For station owner to know his booking
def station_receipt(request):
    current_user = request.user
    owned_stations = station.objects.filter(user=current_user)
    start_date = None
    end_date = None

    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Query the purchase history for records within the specified date range
    station_history = booknow.objects.filter(
        station_id_id__in=owned_stations,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')

    context = {
        'station_history': station_history,
        'start_date': start_date,
        'end_date': end_date,
        # 'total_price': total_price,  # Pass the total_price to the template
    }

    # Render the receipt template to HTML
    template_name = 'station_receipt.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'

    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)

    if not pdf.err:
        response.write(buffer.getvalue())
        return response
    return response


def adm_booking_receipt(request):
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Query the purchase history for records within the specified date range
        booking_history = booknow.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
  
        context = {
            'booking_history': booking_history,
            'start_date': start_date,
            'end_date': end_date,
            # 'total_price': total_price,  # Pass the total_price to the template
        }    


        # Render the receipt template to HTML
        template_name = 'adm_book_receipt.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'
        
        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)

        if not pdf.err:
            response.write(buffer.getvalue())
            return response
        return response

def adm_payment_receipt(request):
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Query the purchase history for records within the specified date range
        payment_history = On_payment.objects.all(
            # date__gte=start_date,
            # date__lte=end_date
        )
  
        context = {
            'payment_history': payment_history,
            'start_date': start_date,
            'end_date': end_date,
            # 'total_price': total_price,  # Pass the total_price to the template
        }    


        # Render the receipt template to HTML
        template_name = 'adm_payment_receipt.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'
        
        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)

        if not pdf.err:
            response.write(buffer.getvalue())
            return response
        return response

def adm_station_receipt(request):
    user_id = request.user.id
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Query the purchase history for records within the specified date range
        station_history = station.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
  
        context = {
            'station_history': station_history,
            'start_date': start_date,
            'end_date': end_date,
            # 'total_price': total_price,  # Pass the total_price to the template
        }    

        # Render the receipt template to HTML
        template_name = 'adm_station_receipt.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'
        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)

        if not pdf.err:
            response.write(buffer.getvalue())
            return response
        return response


def adm_user_receipt(request):
    if request.method == "POST":
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Parse the start and end dates from the form
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Query the purchase history for records within the specified date range
        user_history = CustomUser.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        ).order_by('-date_joined')
  
        context = {
            'user_history': user_history,
            'start_date': start_date,
            'end_date': end_date,
            # 'total_price': total_price,  # Pass the total_price to the template
        }    


        # Render the receipt template to HTML
        template_name = 'adm_user_receipt.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_for_purchases_from_{start_date}_to_{end_date}.pdf"'
        
        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(render_to_string(template_name, context).encode("UTF-8")), buffer)

        if not pdf.err:
            response.write(buffer.getvalue())
            return response
        return response
        # # Calculate the total_price of all orders within the date range
        # total_price = Decimal(0)
        # for history in booking_history:
        #     total_price += history.total_price
    

