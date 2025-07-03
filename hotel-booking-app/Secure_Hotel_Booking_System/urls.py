from django.contrib import admin
from django.urls import path
from My_App import views as my_view
urlpatterns=[
    path("admin/", admin.site.urls),
    path('',my_view.Hotel_Home,name='Hotel_Home'),
    path('About_us/',my_view.About_us,name='About_us'),
    path('Facilities/',my_view.Facilities,name='Facilities'),
    path('My_Room/',my_view.My_Room,name='My_Room'),
    path('Admin_View/',my_view.Admin_View,name='Admin_View'),
    ##############################################################################
    path('my_registration_view/',my_view.registration_view,name='registration_view'),
    path('login/',my_view.login_view, name='login_view'),
    path('logout/',my_view.logout_view,name='logout'),
##########################################################################################################################################################
    path('admin-dashboard/', my_view.admin_dashboard, name='admin_dashboard'),
    ###################################################################################################
    path("add-room-type/",my_view.add_room_type, name="Add_RoomType"),
    path('view-roomtypes/',my_view.View_RoomType, name='View_RoomType'),
    path('search-roomtype/',my_view.search_roomtype, name='search_roomtype'),
    path('update-roomtype/',my_view.update_roomtype, name='update_roomtype'),
    path('delete-roomtype/<int:id>/',my_view.delete_RoomType, name='delete_RoomType'),
    #################################################################################################
    path('manage-rooms/',my_view.Add_Room, name='Add_Room'),
    path('view-room/',my_view.view_room, name='View_Room'),
    path('search-room/',my_view.search_room, name='search_room'),
    path('update-room/',my_view.update_room, name='update_room'),
    path('delete-room/<int:room_id>/',my_view.delete_room, name='delete_room'),
    ########################################################################################################
    path('manage-bookings/',my_view.manage_bookings, name='Add_Booking'),
    path('view-bookings/',my_view.view_bookings, name='view_bookings'),
    #AJAX endpoints
    path('search-booking/',my_view.search_booking, name='search_booking'),
    path('update-booking/',my_view.update_booking, name='update_booking'),
    path('delete-booking/<uuid:booking_id>/',my_view.delete_booking, name='delete_booking'),
    ###################################################################################################
    path('payments/',my_view.add_payment, name='Add_Payment'),
    path('view-payments/',my_view.view_payments, name='view_payments'),
    path('search-payment/',my_view.search_payment, name='search_payment'),
    path('update-payment/',my_view.update_payment, name='update_payment'),
    path('delete-payment/<int:payment_id>/',my_view.delete_payment, name='delete_payment'),
    #################################################################################################################
    ##############################################################################################################
    path('View_role_wise_user/',my_view.View_role_wise_user,name='View_role_wise_user'),
######################################################################################################################################################################
######################################################################################################################################################################
    path('user-dashboard/',my_view.user_dashboard,name='user_dashboard'),
    path('Regularview_room/',my_view.Regularview_room,name='Regularview_room'),
    path('RegularAdd_Booking/',my_view.RegularAdd_Booking,name='RegularAdd_Booking'),
    path('Reqular_Userview_bookings/',my_view.Reqular_Userview_bookings,name='Reqular_Userview_bookings'),
    path('Reqular_Userview_payments/',my_view.Reqular_Userview_payments,name='Reqular_Userview_payments'),
######################################################################################################################################################################
######################################################################################################################################################################


]
