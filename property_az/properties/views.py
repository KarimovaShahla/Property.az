from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import *
from django.contrib import messages
from django.views.generic import DetailView, CreateView
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.views import LoginView


def index(request):
    properties = Property.objects.filter(is_active=True)
    categories = Category.objects.filter(is_main=True, is_sub=False)
    sub_categories = Category.objects.filter(is_main=False, is_sub=False)
    

    liked_properties = []
    if request.user.is_authenticated:
        liked_properties = LikeRelation.objects.filter(user=request.user).values_list('property_id', flat=True)

    context = {
        "categories": categories,
        "sub_categories": sub_categories,
        "properties": properties,
        "liked_properties": liked_properties
    }
    
    return render(request, "properties/index.html", context)


def delete_property_view(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_obj.delete()
    
    return redirect("/")


class PropertyDetailView(DetailView):
    model = Property
    template_name = "properties/property_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()

        liked_properties = []
        if self.request.user.is_authenticated:
            liked_properties = LikeRelation.objects.filter(user=self.request.user).values_list('property_id', flat=True)

        user_liked = property_obj.id in liked_properties if self.request.user.is_authenticated else False
        
        context.update({
            "property_obj": property_obj,
            "user_liked": user_liked
        })

        return context


class PropertyCreateView(CreateView):
    model = Property
    fields = ["title", "description", "price", "category", "city", "district", "address", "area", "rating"]
    template_name = "properties/add_property.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        property_instance = form.instance
        
        images = self.request.FILES.getlist('images')
        for image in images:
            PropertyImage.objects.create(property=property_instance, img=image)
        
        messages.success(self.request, 'Property successfully created!')
        
        user_email = self.request.user.email
        send_mail(
            'Your Property was Successfully Created!',
            f'Thank you for creating a new property listing: {property_instance.title}. You can view your property here: {property_instance.get_absolute_url()}',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        
        return HttpResponseRedirect(reverse('web:property-detail', kwargs={'pk': property_instance.pk}))


def category_properties(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    properties = Property.objects.filter(category=category, is_active=True, status="APPROVED")
    
    context = {
        "category": category,
        "properties": properties
    }
    
    return render(request, "properties/category_properties.html", context)


def user_properties(request, user_id):
    user = get_object_or_404(User, id=user_id)
    properties = Property.objects.filter(user=user, is_active=True, status="APPROVED")
    
    context = {
        "properties": properties
    }
    
    return render(request, "properties/user_properties.html", context)



def like_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    if request.user.is_authenticated:
        like, created = LikeRelation.objects.get_or_create(user=request.user, property=property_obj)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'total_likes': property_obj.total_likes()
        })
    
    return JsonResponse({'error': 'Authentication required'}, status=403)

def send_mail_view(request):
    if request.method == "POST":
        data = request.POST
        to_email = data.get("to")
        subject = data.get("subject")
        product_id = data.get("id")
        
        body = f"""
        Your ad has been accepted, you can view it via the link below:
        http://127.0.0.1:8000/property/{product_id}
        """
        
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False
        )

        return HttpResponse("Email sent successfully!")

    return render(request, "properties/form.html")


class CustomLoginView(LoginView):
    template_name = "properties/login.html"
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "Registr succsessfully!")
        return super().form_valid(form)
