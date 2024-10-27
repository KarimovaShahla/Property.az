from django.urls import path
from .views import *


app_name = 'web'

urlpatterns = [
    path(
        "",
        index,
        name="index"
    ),
    path(
        "property/<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail"
    ),
    path(
        "create-property/",
        PropertyCreateView.as_view(),
        name="create-property"
    ),
    path(
        "delete-property/<int:property_id>/",
        delete_property_view,
        name="delete-property"
    ),
    path(
        "category/<int:category_id>/",
        category_properties,
        name="category-properties"
    ),
     path(
        "user-properties/<int:user_id>/",
        user_properties,
        name="user-properties"
    ),
    path(
        "send-mail/",
        send_mail_view,
        name="send-mail"
    ),
    path(
        "like/<int:property_id>/", 
        like_property, 
        name="like-property"
    ),
    path(
        "login/", 
        CustomLoginView.as_view(), 
        name="login"
    ),
]
