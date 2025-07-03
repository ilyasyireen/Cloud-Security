#########################################################################################################################################################
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
########################################################################====Custom User Manager=======####################################################
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None, user_type=2, **extra_fields):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        extra_fields.setdefault('user_type', 1)  # Admin user type

        user = self.create_user(
            email=email,
            password=password,
            name=name,
            tc=tc,
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        (1, 'Admin'),
        (2, 'Regular User'),
    )

    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=2)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    last_password_change = models.DateTimeField(auto_now=True, editable=False)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        permissions = [
            ("view_own_booking", "Can view only own bookings"),
            ("manage_all_bookings", "Can manage all bookings"),
            ("manage_rooms", "Can manage rooms"),
            ("manage_users", "Can manage users"),
        ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True
        if perm == "view_own_booking":
            return True
        if perm in ["manage_all_bookings", "manage_rooms", "manage_users"]:
            return self.user_type == 1
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_active

    @property
    def is_superuser(self):
        return self.is_admin

    @is_superuser.setter
    def is_superuser(self, value):
        self.is_admin = value

    @property
    def username(self):
        # For legacy compatibility if anything expects `user.username`
        return self.email
#######################################################################################################################################################################################
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    amenities = models.TextField()
    #Security audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_room_types')
    
    def __str__(self):
        return self.name
##############################################################################################################################
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    floor = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    
    # Security fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.room_number} - {self.room_type.name}"
########################################################################################################################################
class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=(
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ), default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Security fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"
############################################################################################################################################
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ), default='pending')
    # Security fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment for {self.booking.booking_id}"
##############################################################################################################################################
class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
    )   
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    table_name = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} {self.action} on {self.table_name} at {self.timestamp}"
################################################################################################################################################
class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=False)
    
    # Security fields
    encrypted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.key
############################################################################################################################################################
