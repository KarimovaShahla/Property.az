import datetime
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    VALUES = (
        (False, "NO"),
        (True, "YES"),
        (None, "UNKNOWN")
         
    )
    super_category = models.ForeignKey("Category", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=64)
    is_main = models.BooleanField(default=False, null=True, blank=True, choices=VALUES)
    is_sub = models.BooleanField(default=False)
    icon = models.ImageField(
        upload_to="uploads/categories/icons/",
        null=True,
        blank=True
        )
    
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"
    
    def get_subcategories(self):
        return Category.objects.filter(super_category=self)
 
    
class City(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}"

class District(models.Model):
    name = models.CharField(max_length=128)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Vendor(models.Model):
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    phone = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name}"


class Property(models.Model):
    STATUSES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(max_length=3000, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=256)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUSES, null=True, blank=True, default="PENDING")
    is_active = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True) #biteceyi vaxti gosterecek



    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.title}"
    
    def save(self, **kwargs):
        if self.expires_at:
            self.check_expiration()

        self.is_active = True if self.is_approved else False

        """if self.status == "REJECTED":
            return self.delete()
"""
        return super().save(**kwargs)
    
    @property
    def is_approved(self):
        return self.status == "APPROVED"
    
    def total_likes(self):
        return self.likerelation_set.count()

    def expire(self):
        self.status = "PENDING"
    
    def check_expiration(self) -> None:
        if self.expires_at < timezone.now():
            self.expire()
    

    def set_expiration(self) -> None:
        if self.expires_at:
           self.expires_at += timedelta(days=30)
        else:
            self.expires_at = timezone.now() + timedelta(days=30)

    def get_absolute_url(self) -> str:
        return reverse("web:property-detail", kwargs={"pk": self.pk})
       
    
    def is_fresh_property(self) -> bool:
        today = datetime.datetime.today()
        return self.created_at + datetime.timedelta(days=30) >= today
    
    def get_thumbnail_image_url(self) -> str:
        image_url = self.images.first()
        if image_url:
            return image_url.img.url
        return ""
    
    def total_likes(self):
        return self.likerelation_set.count() 
    
    def user_liked(self, user):
        return LikeRelation.objects.filter(user=user, property=self).exists()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    img = models.ImageField(upload_to="property_images/%Y/%m/%d/")
    order = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"

    def __str__(self):
        return f"{self.property.title}"
    
class LikeRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "property") 

    def __str__(self):
        return f"{self.user.username} likes {self.property.title}"

