from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

class Driver(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    availability_status = models.BooleanField(default=True)

class FleetOwner(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)