from django.shortcuts import render
from django.http import JsonResponse
from automail import tasks

# Create your views here.

# def test(request):
#     res = tasks.auto_send_mail.delay()
#     return JsonResponse({'status': 'success', 'task_id': res.task_id})
