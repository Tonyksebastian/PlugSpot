from django.shortcuts import render, redirect
from .models import station, booknow, CustomUser,BookingHistory
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required  # viewing all station added
def booking(request):
    stdata = station.objects.filter(hidden=False)
    return render(request, "booking.html", {'stdata': stdata})


# def bookstation(request, station_id):
#     user = request.user
#     user_id = user.id
#     error_message = ''
#     data = station.objects.get(id=station_id)

#     print(data.available)
#     if data.available is None:
#         data.available = data.maxslot
#     data.available = data.available

#     # Retrieve existing booked slot numbers for the station
#     booked_slot_numbers = booknow.objects.filter(station_id=data).values_list('slotnumber', flat=True)
    
#     # Generate a list of available slot numbers
#     available_slot_numbers = [num for num in range(1, data.maxslot + 1) if num not in booked_slot_numbers]

#     if request.method == 'POST':
#         date = request.POST.get('date')
#         time = request.POST.get('time')
#         slotnumber = request.POST.get('your_slot')

#         existing_booking = booknow.objects.filter(
#             date=date, time=time, slotnumber=slotnumber, station_id_id=station_id).first()

#         if existing_booking:
#             error_message = "Slot already booked"
#             return render(request, "booknow.html", {'error': error_message})

#         post = booknow(
#             name=user,  # Assuming 'name' and 'email' are ForeignKey fields in 'booknow'
#             email=user,
#             date=date,
#             time=time,
#             photo=data.photo,
#             slotnumber=slotnumber,
#             stname=data.stname,
#             place=data.place,
#             price=data.price,
#             ownername=data.ownername,
#             station_id_id=data.id
#         )

#         # No need to decrement data.available here
#         data.available -= 1
#         print(data.available)
#         data.save()
#         post.save()

#         return redirect('index')

#     return render(request, "booknow.html", {'available_slot_numbers': available_slot_numbers})


def bookstation(request, station_id):
    user = request.user
    user_id = user.id
    error_message = ''

    data = station.objects.filter(id=station_id)
    data=data[0]
    if data.available is None:
        data.available = data.maxslot

    # Retrieve existing booked slot numbers for the station
    booked_slot_numbers = booknow.objects.filter(
        station_id=data).values_list('slotnumber', flat=True)
    # Generate a list of available slot numbers
    available_slot_numbers = [num for num in range(
        1, data.maxslot + 1) if num not in booked_slot_numbers]

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        slotnumber = request.POST.get('your_slot')

        # Check if the slot is already booked within the specified time range
        existing_booking = booknow.objects.filter(
            date=date,
            station_id_id=station_id,
            slotnumber=slotnumber,
            start_time__lt=end_time,
            end_time__gt=start_time,
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
                station_id_id=data.id
            )
            
            history_entry = BookingHistory(
            name=user,
            email=user,
            date=date,
            time=start_time,  # Set 'time' to the 'start_time'
            start_time=start_time,
            end_time=end_time,
            photo=data.photo,
            slotnumber=slotnumber,
            stname=data.stname,
            place=data.place,
            price=data.price,
            ownername=data.ownername,
            station_id=data,
            status=False  # Set the initial status as False
        )


            # No need to decrement data.available here
            data.available -= 1
            data.save()
            post.save()
            history_entry.save()
            return redirect('index')

    # Check for expired bookings and make slots available
    now = datetime.now()
    expired_bookings = booknow.objects.filter(end_time__lt=now)
    for booking in expired_bookings:
        station1 = booking.station_id
        station1.available += 1  # Increase the available slot count
        station1.save()
        booking.delete()  # Delete the expired booking

    # Retrieve updated available slot numbers after making slots available
    booked_slot_numbers = booknow.objects.filter(station_id=data).values_list('slotnumber', flat=True)
    available_slot_numbers = [num for num in range(1, data.maxslot + 1) if num not in booked_slot_numbers]
    print(available_slot_numbers)
    data.available=len(available_slot_numbers)
    data.save()
    return render(request, "booknow.html", {'available_slot_numbers': available_slot_numbers, 'error': error_message})


def payment(request):
    if request.method == 'POST':
        return redirect('index')
    return render(request, "payment.html")


@login_required
def addstation(request):
    error_message = ''
    user = request.user
    userid = user.id
    stnumber = range(1, 16)
    if request.method == 'POST':
        stname = request.POST.get('stname')
        ownername = request.POST.get('ownername')
        place = request.POST.get('loc')
        contact = request.POST.get('number')
        photo = request.FILES.get('photo')
        latitude = request.POST.get('lat')
        longitude = request.POST.get('long')

        # Retrieve the selected value from the max_slot select element
        maxslot = request.POST.get('max_slot')
        print(maxslot)
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
            description=description,
            price=price,
            user_id=userid
        )
        post.save()

        return redirect("mystation")
    return render(request, "addstation.html", {'stnumber': stnumber})



def mystation(request):
    user_id = request.user.id
    mystation = station.objects.filter(user_id=user_id, hidden=False)
    return render(request, "mystation.html", {'mystation': mystation})


def mybookings(request, station_id=None):
    user_id = request.user.id
    mybookings = booknow.objects.filter(email_id=user_id)
    data = station.objects.filter(id=mybookings[0].station_id.pk).first()  # Use .first() to get a single station
    contact = data.contact  # Assuming 'contact' is the field in the 'station' model

    return render(request, "mybooking.html", {'mybookings': mybookings, 'contact': contact})


def dashboard(request):
    data = CustomUser.objects.all()
    return render(request, "user_dash.html", {'data': data})


def station_dash(request):
    stdata = station.objects.all()
    return render(request, "station_dash.html", {'stdata': stdata})


def update(request, stid2):
    stid = station.objects.get(id=stid2)
    stid1 = station.objects.filter(id=stid2)
    stnumber = range(1, 16)
    if request.method == 'POST':
        stid.stname = request.POST.get('stname')
        stid.ownername = request.POST.get('ownername')
        stid.place = request.POST.get('loc')
        stid.latitude = request.POST.get('lat')
        stid.longitude = request.POST.get('long')
        stid.maxslot = request.POST.get('max_slot',4)
        stid.description = request.POST.get('desc')
        stid.price = request.POST.get('price')

        if 'photo' in request.FILES:
            stid.photo = request.FILES['photo']

        stid.save()
        return redirect("mystation")

    return render(request, 'updatestation.html', {'station': stid1, 'stnumber': stnumber})


# def delete(request, stid2):
#     station_to_hide = station.objects.get(id=stid2)
#     station_to_hide.hidden = True
#     station_to_hide.save()
#     return redirect('mystation')


def delete_items(request, stid2):
    queryset = station.objects.get(id=stid2)
    if request.method == 'POST':
        queryset.hidden = True
        queryset.save()
        return redirect('mystation')
    return render(request, 'mystation.html')

def delete_booking(request, stid2):

    item_to_delete = booknow.objects.get(id=stid2)
    history = BookingHistory.objects.get(id=stid2)
    # stdata=station.objects.all()

    print(item_to_delete.id)
    if request.method == 'POST' and item_to_delete:
        history.status = True
        history.save()

        station_entry = item_to_delete.station_id
        station_entry.available += 1
        station_entry.save()
       
        item_to_delete.delete()
        return redirect('mybookings')
    
    return render(request, 'mybooking.html', {'item_to_delete': item_to_delete})


def delete_adm_user(request,stid2):
    item_to_delete = CustomUser.objects.get(id=stid2)
    item_to_delete.delete()
    return render(request,'user_dash.html')