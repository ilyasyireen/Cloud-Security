from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseForbidden,HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout as auth_logout
from .models import User,UserManager,BaseUserManager,Room,RoomType,Payment,Booking,AuditLog,SystemConfiguration
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.utils.timezone import now
from django.utils.dateparse import parse_date
import uuid
from django.core.paginator import Paginator
import json
from django.views.decorators.http import require_http_methods
################################################################################################################################################################
#####################################################################################################
def Hotel_Home(request):
    return render(request,'My_Home/home.html')
###############################################################################
def About_us(request):
    return render(request,'My_Home/about.html')
########################################################################
def Facilities(request):
    return render(request,'My_Home/Facilities.html')
########################################################################
def My_Room(request):
    return render(request,'My_Home/Room.html')
####################################################################################################################
def Admin_View(request):
    return render(request,'user/Admin_View.html')
#####################################################################################
def registration_view(request):
    """
    Handles user registration based on the custom User model.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password1')
        password2 = request.POST.get('password2')
        tc = request.POST.get('tc') == 'on'  # Convert checkbox to boolean
        user_type = request.POST.get('user_type', '2')  # Default to Regular User
        
        # Basic validation
        if not email or not name:
            messages.error(request, "Email and name are required fields.")
            return redirect('registration_view')
            
        if password != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('registration_view')
            
        if not tc:
            messages.error(request, "You must agree to the terms and conditions.")
            return redirect('registration_view')
            
        try:
            # Check if user already exists
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('registration_view')
                
            # Create user based on type
            if user_type == '1':  # Admin
                user = User.objects.create_superuser(
                    email=email,
                    name=name,
                    tc=tc,
                    password=password
                )
            else:  # Regular user
                user = User.objects.create_user(
                    email=email,
                    name=name,
                    tc=tc,
                    password=password,
                    user_type=2
                )
                
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login_view')
            
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect('registration_view')
    
    # For GET request or if there are errors
    return render(request, 'user/super_registration.html')
###############################################################################################################################
def login_view(request):
    """
    Handles login for Admin and Regular users, supports SweetAlert via AJAX.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Email and password are required.'})
            messages.error(request, "Email and password are required.")
            return redirect('login_view')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                if user.user_type == 1:
                    return JsonResponse({'redirect_url': '/admin-dashboard/'})
                else:
                    return JsonResponse({'redirect_url': '/user-dashboard/'})  # Ensure this view exists

            if user.user_type == 1:
                messages.success(request, f"Welcome Admin {user.name}!")
                return redirect('admin_dashboard')
            else:
                messages.success(request, f"Welcome {user.name}!")
                return redirect('user_dashboard')  # Ensure this view exists
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Invalid email or password.'})
            messages.error(request, "Invalid email or password.")
            return redirect('login_view')

    return render(request, 'user/super_login.html')
##########################################################################################################################################################################
def logout_view(request):
    """
    Handles user logout
    """
    auth_logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login_view')
#############################################################################################################################################################
@login_required
def admin_dashboard(request):
    if request.user.user_type != 1:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    users = User.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()

    context = {
        'user': request.user,
        'users': users,
        'rooms': rooms,
        'students': students,
        'allocate_room': allocate_room,
        'total_students': students.count(),
        'total_rooms': rooms.count(),
        'total_room_allocations': allocate_room.count(),
    }
    return render(request, 'My_Admin/my_admin.html', context)
#############################################################################################################################################################
###########################################################(Room Management)###########################################################
@login_required
def add_room_type(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price_per_night = request.POST.get("price_per_night")
        capacity = request.POST.get("capacity")
        amenities = request.POST.get("amenities")

        if not all([name, description, price_per_night, capacity, amenities]):
            messages.error(request, "All fields are required.")
            return redirect(reverse("Add_RoomType"))

        try:
            price_per_night = float(price_per_night)
            capacity = int(capacity)

            room_type = RoomType(
                name=name,
                description=description,
                price_per_night=price_per_night,
                capacity=capacity,
                amenities=amenities,
                created_by=request.user
            )
            room_type.save()
            messages.success(request, "Room type added successfully!")
            return redirect(reverse("Add_RoomType"))
        except ValueError:
            messages.error(request, "Please enter valid numeric values for price and capacity.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, "My_Admin/RoomType/Add_RoomType.html",
                  {"room_types": room_types,"rooms":rooms,"students":students,"allocate_room":allocate_room})
#######################################################################################################################################
def View_RoomType(request):
    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/RoomType/View_RoomType.html', {'room_types': room_types,
                                                            "rooms":rooms,
                                                            "students":students,
                                                            "allocate_room":allocate_room})
#########################################################################################################################################
def search_roomtype(request):
    name = request.GET.get('name')
    if not name:
        return JsonResponse({
            "status": "error",
            "message": "Room type name is required."
        })

    try:
        room = RoomType.objects.get(name__iexact=name)
        return JsonResponse({
            "status": "success",
            "room": {
                "description": room.description,
                "price_per_night": str(room.price_per_night),
                "capacity": room.capacity,
                "amenities": room.amenities
            }
        })
    except RoomType.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Room Type not found."
        })

@csrf_exempt  # Ensure CSRF token is used in frontend for production
def update_roomtype(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            return JsonResponse({"status": "error", "message": "Room type name is required."})

        try:
            room = RoomType.objects.get(name__iexact=name)
            room.description = request.POST.get("description", "")
            room.price_per_night = request.POST.get("price_per_night") or 0.0
            room.capacity = request.POST.get("capacity") or 0
            room.amenities = request.POST.get("amenities", "")
            room.save()

            return JsonResponse({
                "status": "success",
                "message": "Room Type updated successfully."
            })

        except RoomType.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Room Type not found."
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method."
    })
############################################################################################################################################
def delete_RoomType(request, id):
    room = get_object_or_404(RoomType, id=id)
    room.delete()
    return redirect('View_RoomType')
############################################################################################################################################
###########################################################(Manage Rooms)##################################################################
def Add_Room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type_id = request.POST.get('room_type')
        floor = request.POST.get('floor')
        is_available = request.POST.get('is_available') == 'True'

        try:
            room_type = RoomType.objects.get(id=room_type_id)
            new_room = Room(
                room_number=room_number,
                room_type=room_type,
                floor=floor,
                is_available=is_available
            )
            new_room.save()
            messages.success(request, 'Room added successfully!')
        except RoomType.DoesNotExist:
            messages.error(request, 'Invalid room type selected.')
        except IntegrityError:
            messages.error(request, 'Room number must be unique.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('Add_Room')

    rooms = Room.objects.select_related('room_type').order_by('-id')
    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/Room/Add_Room.html', {
        'rooms': rooms,
        'room_types': room_types,
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
######################################################################################################################################
def view_room(request):
    rooms = Room.objects.filter(is_deleted=False)
    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/Room/View_Room.html', {
        'rooms': rooms,
        'room_types': room_types,
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })

def search_room(request):
    room_number = request.GET.get('room_number')
    try:
        room = Room.objects.select_related('room_type').get(room_number=room_number, is_deleted=False)
        return JsonResponse({
            'status': 'success',
            'room': {
                'room_number': room.room_number,
                'room_type_id': room.room_type.id,
                'floor': room.floor,
                'is_available': str(room.is_available)  # Send as string to match HTML values
            }
        })
    except Room.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Room not found'})

@csrf_exempt
def update_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_type_id = request.POST.get('room_type_id')  # Must match JS key
        floor = request.POST.get('floor')
        is_available = request.POST.get('is_available') == 'True'  # Capital T

        try:
            room = Room.objects.get(room_number=room_number, is_deleted=False)
            room.room_type_id = room_type_id
            room.floor = floor
            room.is_available = is_available
            room.save()
            return JsonResponse({'status': 'success', 'message': 'Room updated successfully'})
        except Room.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Room not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def delete_room(request, room_id):
    try:
        room = get_object_or_404(Room, pk=room_id, is_deleted=False)
        room.is_deleted = True
        room.deleted_at = now()
        room.save()
        return JsonResponse({'status': 'success', 'message': 'Room deleted successfully'})
    except:
        return JsonResponse({'status': 'error', 'message': 'Room not found or already deleted'})
####################################################################################################################################################
def manage_bookings(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        room_id = request.POST.get('room')
        check_in = request.POST.get('check_in_date')
        check_out = request.POST.get('check_out_date')
        total_price = request.POST.get('total_price')
        status = request.POST.get('status', 'confirmed')

        if not all([user_id, room_id, check_in, check_out, total_price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('Add_Booking')

        try:
            user = User.objects.get(id=user_id)
            room = Room.objects.get(id=room_id)

            Booking.objects.create(
                user=user,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                total_price=total_price,
                status=status
            )

            messages.success(request, "Booking added successfully.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    # GET method
    users = User.objects.all()
    rooms = Room.objects.filter(is_available=True, is_deleted=False)
    bookings = Booking.objects.all().order_by('-created_at')
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/Booking/Add_Booking.html', {
        'users': users,
        'rooms': rooms,
        'bookings': bookings,
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
##################################################################################################################################################
def view_bookings(request):
    bookings = Booking.objects.filter(is_deleted=False).select_related('user', 'room')
    users = User.objects.all()
    rooms = Room.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/Booking/View_Booking.html', {
        'bookings': bookings,
        'users': users,
        'rooms': rooms,
        "students":students,
        "allocate_room":allocate_room
    })

def search_booking(request):
    booking_id = request.GET.get("booking_id")
    try:
        booking = Booking.objects.get(booking_id=booking_id, is_deleted=False)
        return JsonResponse({
            "status": "success",
            "booking": {
                "user_id": booking.user.id,
                "room_id": booking.room.id,
                "check_in_date": booking.check_in_date.strftime('%Y-%m-%d'),
                "check_out_date": booking.check_out_date.strftime('%Y-%m-%d'),
                "total_price": float(booking.total_price),
                "status": booking.status
            }
        })
    except Booking.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Booking not found."})

@csrf_exempt
def update_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get("booking_id")
        try:
            booking = Booking.objects.get(booking_id=booking_id, is_deleted=False)
            booking.user_id = request.POST.get("user_id")
            booking.room_id = request.POST.get("room_id")
            booking.check_in_date = parse_date(request.POST.get("check_in_date"))
            booking.check_out_date = parse_date(request.POST.get("check_out_date"))
            booking.total_price = request.POST.get("total_price")
            booking.status = request.POST.get("status")
            booking.save()
            return JsonResponse({"status": "success", "message": "Booking updated successfully."})
        except Booking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found."})
    return JsonResponse({"status": "error", "message": "Invalid request."})

def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    booking.delete()  # Permanently delete
    return redirect('view_bookings')
#################################################################################################################################################################
def add_payment(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking')
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        status = request.POST.get('status')

        # Check if payment already exists for the booking
        if Payment.objects.filter(booking_id=booking_id).exists():
            messages.error(request, 'Payment already exists for this booking.')
            return redirect('Add_Payment')

        try:
            booking = Booking.objects.get(id=booking_id)
            Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method=method,
                transaction_id=transaction_id,
                status=status,
                deleted_at=None  # Or use timezone.now() only if you're marking deleted payments
            )
            messages.success(request, 'Payment added successfully.')
        except Booking.DoesNotExist:
            messages.error(request, 'Invalid booking selected.')

        return redirect('Add_Payment')

    else:
        bookings = Booking.objects.all()
        payments = Payment.objects.all().order_by('-payment_date')
        rooms = Room.objects.all()
        students = Booking.objects.all()
        allocate_room = RoomType.objects.all()
        return render(request, 'My_Admin/Payment/Add_Payment.html', {
            'bookings': bookings,
            'payments': payments,
            "rooms":rooms,
            "students":students,
            "allocate_room":allocate_room
        })
#############################################################################################################################################
def view_payments(request):
    payments = Payment.objects.filter(is_deleted=False).select_related('booking')
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'My_Admin/Payment/View_Payment.html', {
        'payments': payments,
        'bookings': Booking.objects.all(),
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
#################################################################################################
def search_payment(request):
    booking_id = request.GET.get('booking_id')
    try:
        payment = Payment.objects.select_related('booking').get(booking__booking_id=booking_id, is_deleted=False)
        return JsonResponse({
            'status': 'success',
            'payment': {
                'amount': str(payment.amount),
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.status
            }
        })
    except Payment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Payment not found'})
##############################################################################################
def update_payment(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        try:
            payment = Payment.objects.get(booking__booking_id=booking_id)
            payment.amount = request.POST.get('amount')
            payment.payment_method = request.POST.get('payment_method')
            payment.transaction_id = request.POST.get('transaction_id')
            payment.status = request.POST.get('status')
            payment.save()
            return JsonResponse({'status': 'success', 'message': 'Payment updated successfully'})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
####################################################################################################
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.is_deleted = True
    payment.save()
    return redirect('view_payments')
#######################################################################################################################################


####################################################################################################################################
def View_role_wise_user(request):
    """
    View for the admin dashboard that groups users by specific roles
    (Admin, Staff, Student) and passes the data to the template.
    """
    # Define user role mapping based on `user_type` and flags
    grouped_users = {
        'Admin': User.objects.filter(user_type=1),  # Admins
        'Regular User': User.objects.filter(user_type=2),  # Regular Users (Staff or Students)
    }
    grouped_users["No Role Assigned"] = User.objects.filter(user_type__isnull=True)
    #Additional context
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    # Render the template
    return render(
        request,
        'My_Admin/User/Role_Wise_User.html',
        {
            'grouped_users': grouped_users,
            "rooms": rooms,
            "students": students,
            "allocate_room": allocate_room
        }
    )
#############################################################################################################################################################33
#############################################################################################################################################################33
@login_required
def user_dashboard(request):
    if request.user.user_type == 1:
        return HttpResponseForbidden("Admins are not allowed to view this page.")
    # Assuming user_type = 2 is a Regular User (as per your model)
    regular_users = User.objects.filter(user_type=2)
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    context = {
        'regular_users': regular_users,
        'total_regular_users': regular_users.count(),
        'current_user': request.user,
        'rooms': rooms,
        'students': students,
        'allocate_room': allocate_room,
        'total_students': students.count(),
        'total_rooms': rooms.count(),
        'total_room_allocations': allocate_room.count(),
    }
    return render(request, 'Reqular_User/my_reqularuser.html', context)
################################################################################################################
def Regularview_room(request):
    rooms = Room.objects.filter(is_deleted=False)
    room_types = RoomType.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request,'Reqular_User/Room/View_Room.html', {
        'rooms': rooms,
        'room_types': room_types,
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
##########################################################################################################
def RegularAdd_Booking(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        room_id = request.POST.get('room')
        check_in = request.POST.get('check_in_date')
        check_out = request.POST.get('check_out_date')
        total_price = request.POST.get('total_price')
        status = request.POST.get('status', 'confirmed')

        if not all([user_id, room_id, check_in, check_out, total_price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('RegularAdd_Booking')

        try:
            user = User.objects.get(id=user_id)
            room = Room.objects.get(id=room_id)

            Booking.objects.create(
                user=user,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                total_price=total_price,
                status=status
            )

            messages.success(request, "Booking added successfully.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    # GET method
    users = User.objects.all()
    rooms = Room.objects.filter(is_available=True, is_deleted=False)
    bookings = Booking.objects.all().order_by('-created_at')
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request,'Reqular_User/Booking/Add_Booking.html', {
        'users': users,
        'rooms': rooms,
        'bookings': bookings,
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
############################################################################################################
def Reqular_Userview_bookings(request):
    bookings = Booking.objects.filter(is_deleted=False).select_related('user', 'room')
    users = User.objects.all()
    rooms = Room.objects.all()
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'Reqular_User/Booking/View_Booking.html', {
        'bookings': bookings,
        'users': users,
        'rooms': rooms,
        "students":students,
        "allocate_room":allocate_room
    })
##################################################################################################################
def Reqular_Userview_payments(request):
    payments = Payment.objects.filter(is_deleted=False).select_related('booking')
    rooms = Room.objects.all()
    students = Booking.objects.all()
    allocate_room = RoomType.objects.all()
    return render(request, 'Reqular_User/Payment/View_Payment.html', {
        'payments': payments,
        'bookings': Booking.objects.all(),
        "rooms":rooms,
        "students":students,
        "allocate_room":allocate_room
    })
#########################################################################################################################
