from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from vect_db import user_chat_ai, api_keys_gorq_pinecone


@login_required
def gen_ai_chat(request):
    """
    View for handling chat message and returning AI response.
    :param request:
    :return: Template with AI response.
    """
    response = None

    if request.method == 'POST':
        message = request.POST.get('message')
        api_keys = request.user.ai_creds.filter(is_active=True).first()
        if api_keys:
            pc, database_name, pinecone_index, client = api_keys_gorq_pinecone(
                api_keys.pinecone_api_key,
                api_keys.pinecone_index_name,
                api_keys.groq_api_key)
        else:
            pc, database_name, pinecone_index, client = api_keys_gorq_pinecone()
        gen_ai_response = user_chat_ai(message, pc, pinecone_index, client)
        response = f"AI Response to your message: {gen_ai_response}"
    return render(request, 'ai_chat.html', {'response': response})
