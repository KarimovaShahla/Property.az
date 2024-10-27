from django.core.mail import send_mail
from django.conf import settings
from properties.models import Property


def send_mail_func(data:dict):
    to_email = "shehla.kerimova98@gmail.com"
    subject = "Kitab"
    product_id = data.get("id", 888)
    product = Property.objects.get(id=product_id)
    url = product.get_absolute_url()

    body = f"""
        Your ad has been accepted, you can view it via the link below:
        127.0.0.1:8000{url}
    """

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False
    )
       


   
