from django.shortcuts import render
from vect_db import user_chat_ai


def gen_ai_chat(request):
    """
    View for handling chat message and returning AI response.
    :param request:
    :return: Template with AI response.
    """
    response = None

    if request.method == 'POST':
        message = request.POST.get('message')
        gen_ai_response = user_chat_ai(message)
        response = f"AI Response to your message: {gen_ai_response}"

    return render(request, 'ai_chat.html', {'response': response})
