import os, time
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task, task
from celery import app
from django_demo import settings
from django.core.mail import send_mail


@task()
def auto_send_mail():
    subject = "test subject"
    message = "Message"
    recipient_list = ['13551296510@163.com']
    print("======发送邮件======")
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list, fail_silently=False)
