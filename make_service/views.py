from audioop import reverse
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

# Create your views here.
from datetime import datetime
from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import service_station, add_service,service_booking, AdditionalService, CustomUser, add_package, Favorite,Feedback
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Q
from bs4 import BeautifulSoup
import requests
# Create your views here.


@login_required
def addservicestation(request):
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
        date = datetime.now()
        description = request.POST.get('desc')

        descriptions = ','.join(description.split('\n'))

        post = service_station(
            stname=stname,
            place=place,
            photo=photo,
            ownername=ownername,
            latitude=latitude,
            contact=contact,
            longitude=longitude,
            maxslot=maxslot,
            date=date,
            available=available,
            description=descriptions,
            user_id=userid
        )
        post.save()
        post2= Favorite(
            station_id_id=post.id,
            user_id=userid
        )        
        post2.save()

        return redirect('subscription')
    return render(request, "addservicestation.html", {'stnumber': stnumber})


def add_services(request, ser_id):
    user = request.user
    userid = user.id
    if request.method == 'POST':
        photo = request.FILES.get('ser_img')
        ser_name = request.POST.get('ser_name')
        desc = request.POST.get('ser_desc')
        price = request.POST.get('ser_price')

        post = add_service(
            photo=photo,
            ser_name=ser_name,
            description=desc,
            price=price,
            service_id=ser_id,
            name_id=userid
        )
        post.save()

        return redirect('select_station')
    return render(request, "add_services.html",)


def update_services(request, service_id):
    user = request.user
    userid = user.id
    
    # Fetch the service object to update
    service = get_object_or_404(add_service, id=service_id)

    if request.method == 'POST':
        # Update the service with new data from the form
        service.photo = request.FILES.get('ser_img')
        service.ser_name = request.POST.get('ser_name')
        service.description = request.POST.get('ser_desc')
        service.price = request.POST.get('ser_price')
        service.save()

        return redirect('myservice_station')
    
    # Pass the service object to the template for rendering the update form
    return render(request, "update_service.html", {'service': service})


def toggle_service_visibility(request, service_id, station_id):
    # Retrieve the service object
    service = get_object_or_404(add_service, id=service_id)

    service.status = not service.status
    service.save()

    # Redirect back to the services page with the station_id as ser_id
    return redirect('services', ser_id=station_id)


def service_home(request):
    return render(request, 'services_home.html')


def contact(request):
    return render(request, 'contact.html')

from django.db.models import Avg
def select_station(request):
    stations = service_station.objects.filter(hidden=False).order_by("-date")
    for station in stations:
        if station.description:
            station.descriptions_list = station.description.split(',')
        else:
            station.descriptions_list = []
        
        # Calculate the average rating for the station
        station.average_rating = Feedback.objects.filter(station=station).aggregate(avg_rating=Avg('rating'))['avg_rating']
        
    return render(request, "servicestation_list.html", {'stations': stations})

def services(request, ser_id):
    userid= request.user.id
    stations = service_station.objects.all().order_by("-date")
    if request.user.role == "vhowner":  # Assuming the user's role is stored in request.user.role
        ser_data = add_service.objects.filter(service_id=ser_id, status=False)  # Fix the model name
        print(ser_id)
        return render(request, "bookservice.html", {'ser_data': ser_data, 'ser_id': ser_id,'stations': stations})
    
    else:
        ser_data = add_service.objects.filter(service_id=ser_id, delete_status = False)  # Fix the model name
        return render(request, "bookservice.html", {'ser_data': ser_data, 'ser_id': ser_id,'userid':userid, 'stations': stations})


def service_station_list(request):
    user=request.user
    stations = service_station.objects.all().order_by("-date")
    favorite_id= Favorite.objects.filter(user=user,is_favorite = True)
    list1=[]
    for i in favorite_id:
        list1.append(i.station_id_id)
    print(list1)
    
    return render(request, "servicestation_list.html", {'stations': stations,'favorites_id':list1})

def myfavservicest(request):
    user = request.user.id
    fav = Favorite.objects.filter(user=user,is_favorite=True)
    return render(request, "myfavorite_servicestation.html", {'data': fav})


def myservice_station(request):
    user_id = request.user.id
    mystation = service_station.objects.filter(user_id=user_id, hidden=False)
    return render(request, "myservice_station.html", {'mystation': mystation})


@login_required
def bookservice(request, service_id):
    error_message = ''
    available_slots = []
    
    # Get the service station
    servicestation1 = add_package.objects.get(id=service_id)
    maxslot = servicestation1.service.service.available

    # Generate available slots
    for i in range(1, maxslot + 1):
        available_slots.append(i)
    
    if request.method == 'POST':
        company = request.POST.get('company')
        model = request.POST.get('model')
        km = request.POST.get('km')
        date = request.POST.get('date')
        book_desc = request.POST.get('book_desc')
        slotnumber = request.POST.get('your_slot')
        vehno = request.POST.get('vehicle_number')

        # Create a new booking
        booking = service_booking(
            company=company,
            model=model,
            vehno=vehno,
            km_done=km,
            date=date,
            desc=book_desc,
            time=timezone.now(),
            slotnumber=slotnumber,
            package_id=service_id,
            user=request.user
        )
        booking.save()

        addService = add_service.objects.get(id=servicestation1.service_id)
        station = service_station.objects.get(id=addService.service_id)
        station.available = station.available - 1
        station.save()

        send_service_booking_email(request.user.email, booking)
        return redirect('ser_book_success')

    return render(request, "service_booking_form.html", {'available_slots': maxslot, 'error_message': error_message})

def send_service_booking_email(user_email, booking):
    # Fetch the associated service package
    package = add_package.objects.get(id=booking.package_id)
    if package:
        # Fetch the associated service
        service = add_service.objects.get(id=package.service_id)
        if service:
            # Fetch the associated service station
            station = service_station.objects.get(id=service.service_id)
            if station:
                email_subject = 'Service Booking Confirmation'
                email_body = f'''
                    Dear {booking.user.first_name},
                    
                    Your service booking has been confirmed successfully. Below are the details of your booking:
                    
                    Owner Name: {station.ownername}
                    Phone: {station.contact}
                    Company: {booking.company}
                    Model: {booking.model}
                    KM Done: {booking.km_done}
                    Date: {booking.date}
                    Time: {booking.time}
                    Slotnumber: {booking.slotnumber}
                    Thank you for choosing our service!
                '''
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user_email]

                email = EmailMessage(email_subject, email_body, from_email, recipient_list)
                email.send()
            else:
                print("Service station not found for the booking.")
        else:
            print("Service not found for the booking.")
    else:
        print("Service package not found for the booking.")


def ser_book_success(request):
    return render(request,"ser_book_success.html")




def attend_service_booking(request, booking_id):
    print('hello')
    booking = get_object_or_404(service_booking, id=booking_id)
    booking.status = True
    booking.save()
        # Redirect to the worker dashboard or another page
    return redirect('worker_dash')
    

def hide_ser_station(request,stid3):

    station_to_hide = service_station.objects.get(id=stid3)
    station_to_hide.hidden=True
    station_to_hide.save()
    return redirect('myservice_station')

def show_serstation(request, stid2):
    station_to_hide = get_object_or_404(service_station, id=stid2)
    station_to_hide.hidden = False
    station_to_hide.save()
    return redirect('myservice_station')

def closed_service_station(request):
    user_id = request.user.id
    mystation = service_station.objects.filter(user_id=user_id, hidden=True)
    return render(request, "service_shutdown.html", {'mystation': mystation})


def ser_update(request, stid2):
    myStation = service_station.objects.get(id=stid2)
    if request.method == 'POST':
        # Update the fields of the station object with the submitted data
        myStation.stname = request.POST.get('stname')
        myStation.ownername = request.POST.get('ownername')
        myStation.place = request.POST.get('place')
        myStation.latitude = request.POST.get('latitude')
        myStation.longitude = request.POST.get('longitude')
        myStation.maxslot = request.POST.get('maxslot')
        myStation.description = request.POST.get('description')
        myStation.contact = request.POST.get('contact')
        myStation.save()
        return redirect('myservice_station')
    else:
        return render(request, "ser_station_update.html", {'myStation': myStation})

def ser_delete(request, stid2):
    station_to_hide = get_object_or_404(service_station, id=stid2)
    station_to_hide.hidden = True
    station_to_hide.save()
    return redirect('myservice_station')

def delete_service(request, service_id):
    service_to_hide = get_object_or_404(add_service, id=service_id)
    service_to_hide.status = True
    service_to_hide.delete_status = True
    service_to_hide.save()
    return redirect('myservice_station')

def delete_mybookservice(request, service_id):

    service_to_delete = get_object_or_404(service_booking, id=service_id)
    
    # Create an aware datetime for the booking date and time
    booking_datetime = timezone.make_aware(
        timezone.datetime.combine(service_to_delete.date, service_to_delete.time)
    )
    
    # Calculate the time difference between now and the booking date and time
    time_difference = timezone.now() - booking_datetime
    
    # Calculate the time difference in seconds
    time_difference_seconds = time_difference.total_seconds()
    
    
    # Check if the time difference is greater than 24 hours (86400 seconds)
    if time_difference_seconds > 24 * 3600:
        # If yes, set del_status to True and save the booking
        print(time_difference_seconds)

        service_to_delete.del_status = True
        service_to_delete.save()
        return redirect('mybooking')
    
    else:
        # If no, render a template with the warning message in a modal
        return render(request, 'warning_modal.html')
    
    
def mybooking(request):
    user_id = request.user.id
    booked_data = service_booking.objects.filter(user_id=user_id,del_status = False).order_by('-date')
    return render(request, "service_booked.html", {'booked_data': booked_data})


def service_packages(request, service_id):
    # Filter packages based on the service ID
    packages = add_package.objects.filter(service__id=service_id, package_del_status=False)

    # Extract package descriptions and create a list
    package_desc_list = []
    for package in packages:
        desc_split = package.package_desc.split(', ')
        package_desc_list.extend(desc_split)

    return render(request, "service_packages.html", {'packages': packages, 'package_desc_list': package_desc_list})


def add_packages(request, service_id):
    user = request.user.id
    if request.method == 'POST':
        # Extract data from the form
        package_name = request.POST.get('pkg_name')
        duration = request.POST.get('pkg_duration')
        package_desc_str = request.POST.get('pkg_services')
        orginal_price = request.POST.get('org_price')
        discount_price = request.POST.get('dic_price')
        package_image = request.FILES.get('pkg_image')

        package_desc_list = [desc.strip() for desc in package_desc_str.split(',')]

        # Save data to the add_package model
        new_package = add_package.objects.create(  # Use objects.create to create a new instance
            package_name=package_name,
            duration=duration,
            package_desc=", ".join(package_desc_list),
            orginal_price=orginal_price,
            discount_price=discount_price,
            package_image=package_image,
            name_id=user,
            service_id=service_id
        )

        # Redirect to a success page or any other page
        return redirect('service_packages', service_id=service_id)  # Pass service_id to redirect
    else:
        return render(request, "add_packages.html")

def completed(request, book_id):
        
    booked_data = service_booking.objects.get(id=book_id)
    available=booked_data.package.service.service
    available.available=+1        
    booked_data.completed = True
    booked_data.save()
    available.save()    
    return redirect(worker_dash)


    
def update_packages(request, package_id):
    package = get_object_or_404(add_package, id=package_id)

    if request.method == 'POST':
        # Extract data from the form
        pkg_name = request.POST.get('pkg_name')
        pkg_duration = request.POST.get('pkg_duration')
        pkg_services = request.POST.get('pkg_services')
        org_price = request.POST.get('org_price')
        dic_price = request.POST.get('dic_price')
        pkg_image = request.FILES.get('pkg_image')

        # Update package data
        package.package_name = pkg_name
        package.duration = pkg_duration
        package.package_desc = pkg_services
        package.orginal_price = org_price
        package.discount_price = dic_price
        if pkg_image:
            package.package_image = pkg_image
        package.save()

        # Redirect to service_packages with the corresponding service ID
        return redirect('service_packages', service_id=package.service.id)
    else:
        return render(request, "update_package.html", {'package': package})
    
def delete_package(request, package_id):
    # Retrieve the package and its associated service ID
    package = get_object_or_404(add_package, id=package_id)
    service_id = package.service_id
    
    # Update the package's delete status
    package.package_del_status = True
    package.save()
    
    # Redirect to the service packages page with the associated service ID
    return redirect('service_packages', service_id=service_id)


def toggle_add_favorite(request, station_id):
    user = request.user
    station = get_object_or_404(service_station, id=station_id)
    
    # Check if the station is already in favorites
    fav = Favorite.objects.get(user=user, station_id_id=station_id)
    print(fav)
    # If the favorite already exists, set is_favorite to True
    fav.is_favorite = True
    fav.save()
    
    return redirect('service_station_list')


def toggle_rem_favorite(request, station_id):
    print(station_id)
    user = request.user
    fav=Favorite.objects.get(user_id=user.id,station_id_id=station_id)
    if fav.is_favorite:
        fav.is_favorite = False
    fav.save()
    return redirect('service_station_list')

def detailed_book_data(request, booking_id):
    # Retrieve booking object from the database
    booking = service_booking.objects.get(id=booking_id)    
    # Calculate the initial package cost
    pkg_cost = booking.package.discount_price
    
    # Calculate the total cost of additional services
    additional_services_cost = 0
    additional_services = AdditionalService.objects.filter(booking_id=booking_id)
    for service in additional_services:
        additional_services_cost += service.cost

    # Calculate the total cost (package cost + additional services cost)
    total_cost = pkg_cost + additional_services_cost

    if request.method == 'POST':
        # Process form data to add additional services to the booking
        additional_service_name = request.POST.get('additional_service')
        service_cost = request.POST.get('service_cost')

        # Check if service_cost is not None and not an empty string
        if service_cost and service_cost.strip():
            # Create new additional service object and associate it with the booking
            additional_service = AdditionalService.objects.create(
                name=additional_service_name,
                cost=float(service_cost),
                booking=booking
            )

            # Update the total cost for the booking
            total_cost += float(service_cost)
            additional_service.total_cost = total_cost
            additional_service.save()

            # Redirect back to the booking details page to avoid form resubmission
            return redirect('detailed_book_data', booking_id=booking_id)

    # Render the template with booking details and total cost
    return render(request, 'booked_service_worker.html', {'booking': booking,'total_cost': total_cost})

def delete_added_work(request, service_id):
    # Retrieve the AdditionalService object to be deleted
    service = get_object_or_404(AdditionalService, id=service_id)
    
    # Delete the service
    service.delete()
    
    # Redirect to a relevant page (e.g., booking details page)
    return redirect('detailed_book_data', booking_id=service.booking.id)


def feedback_page(request, ser_id):
    
    user_id = request.user.id
    feedbacks = Feedback.objects.filter(station_id=ser_id,status=False).order_by("-date")
    return render(request, 'feedback.html', {'feedbacks': feedbacks,'station_id':ser_id,'user_id':user_id})

def add_comment(request, ser_id):
    user_id = request.user.id

    if request.method == 'POST':
        message = request.POST.get('messages')
        rating = request.POST.get('rating')        # Fetch the CustomUser object using the user ID
        user = CustomUser.objects.get(id=user_id)

        # Create the Feedback object
        feedback = Feedback.objects.create(
            userprofile_id=user_id,
            station_id=ser_id,
            first_name=user.first_name,
            last_name=user.last_name,
            message=message,
            rating=rating,  
            status=True,
            date=datetime.now(),
        )
        feedback.save()

    # Redirect to the feedback_page with the station_id
    return redirect('feedback_page', ser_id=ser_id)


def delete_feedback(request, feedback_id, ser_id):
    # Retrieve the feedback object
    user_id = request.user.id
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    
    # Set status to True to mark as deleted
    feedback.status = True
    feedback.save()  # Save the changes
    
    # Redirect to the feedback page with both station_id and user_id
    return redirect('feedback_page', ser_id=ser_id)


# def cart(request):
#     return render(request,"cart.html")

# def add_to_cart(request):
#     if request.method == 'POST':
#         # Assuming you have form data or other means to get package_id and service_id
#         package_id = request.POST.get('package_id')
#         service_id = request.POST.get('service_id')
        
#         # Get the current user
#         user = request.user
        
#         # Create a new cart instance
#         new_cart = cart.objects.create(
#             package_id=package_id,
#             service_id=service_id,
#             user=user,
#             status=False,  # Assuming you want to set status to False by default
#             completed=False,  # Similarly for completed
#             payment_done=False  # Similarly for payment_done
#         )
        
#         # Save the new cart instance
#         new_cart.save()
        
#         return render(request, "cart.html")
    


from bs4 import BeautifulSoup
import requests

def car_guide_view(request):
    # URL of the website you want to scrape
    url = "https://www.tatacapital.com/blog/loan-for-vehicle/charging-safety-guidelines-for-electric-vehicles/"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all <div> elements with class name 'detail_content bg_white'
    containers = soup.find_all('div', class_='detail_content bg_white')
    
    # Initialize lists to store formatted content for each tag
    formatted_strong = []
    formatted_li = []
    formatted_p = []
    formatted_h1 = []
    formatted_h2 = []
    
    # Iterate over each container
    for container in containers:
        # Extract and format content from <strong> tags
        strong_tags = container.find_all('strong')
        for tag in strong_tags:
            formatted_strong.append(tag.text.strip())
        
        # Extract and format content from <li> tags
        li_tags = container.find_all('li')
        for tag in li_tags:
            formatted_li.append(tag.text.strip())
        
        # Extract and format content from <p> tags
        p_tags = container.find_all('p')
        for tag in p_tags:
            formatted_p.append(tag.text.strip())
        
        # Extract and format content from <h1> tags
        h1_tags = container.find_all('h1')
        for tag in h1_tags:
            formatted_h1.append(tag.text.strip())
        
        # Extract and format content from <h2> tags
        h2_tags = container.find_all('h2')
        for tag in h2_tags:
            formatted_h2.append(tag.text.strip())
    
    # Pass the formatted information to the template
    return render(request, 'webscrap.html', {
        'formatted_strong': formatted_strong,
        'formatted_li': formatted_li,
        'formatted_p': formatted_p,
        'formatted_h1': formatted_h1,
        'formatted_h2': formatted_h2
    })


def complted_worker_dash(request):
    user = request.user
    data = CustomUser.objects.filter(id=user.id)
    total_booking = service_booking.objects.filter(status=True).count()
    bookings = service_booking.objects.filter(payment_done=True)
    return render(request, "completed_worker_dashboard.html", {'bookings': bookings, 'data': data, 'total_booking': total_booking})

def worker_dash(request):
    user = request.user
    data = CustomUser.objects.filter(id=user.id)
    total_booking = service_booking.objects.filter(status=True).count()
    bookings = service_booking.objects.all()
    return render(request, "worker_dashboard.html", {'bookings': bookings, 'data': data, 'total_booking': total_booking})

def myservice_station_bookings(request):
    return render(request,"myservice_station_booking.html")