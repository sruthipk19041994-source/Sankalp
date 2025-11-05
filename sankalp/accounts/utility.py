from twilio.rest import Client
from decouple import config
from twilio.rest import Client
from decouple import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import render_to_string




def send_phone_sms(phone_num, message):
    """
    Sends an SMS using Twilio.
    In demo mode, all messages go to a static number for safety.
    """
    try:
        account_sid = config('ACCOUNT_SID')
        auth_token = config('AUTH_TOKEN')
        from_num = config('FROM_NUM')

        # ✅ Always use this static dummy number for testing
        demo_num = '+919061525199'

        client = Client(account_sid, auth_token)
        client.messages.create(
            from_=from_num,
            body=message,
            to=demo_num  # 👈 Replaced dynamic number with demo number
        )
        print(f"✅ SMS sent (Demo Mode) to {demo_num}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")

from accounts.models import Profile, Notification  # add at top where other imports are

def create_notification(profile_or_profile_id, message):
    """
    Create a DB notification for a Profile instance or profile id.
    Example usages:
      create_notification(request.user.profile, "New request submitted")
      create_notification(profile_id, "Please review")
    """
    try:
        if isinstance(profile_or_profile_id, int):
            profile = Profile.objects.get(id=profile_or_profile_id)
        else:
            profile = profile_or_profile_id
        Notification.objects.create(recipient=profile, message=message)
        # optionally return the created object if needed
    except Exception as e:
        # fail silently for now (log in console) so UI flow won't break
        print(f"⚠️ create_notification failed: {e}")


def sending_email(subject,template,context,recipient):

    sender = settings.EMAIL_HOST_USER

    email_obj=EmailMultiAlternatives(subject,from_email=sender,to=[recipient])

    content = render_to_string(template,context)

    email_obj.attach_alternative(content,'text/html')

    email_obj.send()

