from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from core.constants import *


@login_required(login_url='login')
def public_chat_page_view(request):
	context = {
		'debug_mode': settings.DEBUG,
		'room_id': PUBLIC_CHAT_ROOM_ID, 
	}

	return render(request, 'public_chat/public_chat_page.html', context)