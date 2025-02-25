from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime

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


@login_required
def my_uploads(request):
    """
    View for displaying user's uploaded documents from Pinecone.
    :param request:
    :return: Template with list of uploads.
    """
    api_keys = request.user.ai_creds.filter(is_active=True).first()
    if api_keys:
        pc, database_name, pinecone_index, client = api_keys_gorq_pinecone(
            api_keys.pinecone_api_key,
            api_keys.pinecone_index_name,
            api_keys.groq_api_key)
    else:
        pc, database_name, pinecone_index, client = api_keys_gorq_pinecone()
    
    # Fetch all vectors (documents) from the index
    total_vectors = pinecone_index.describe_index_stats()['total_vector_count']
    vector_ids = [str(i) for i in range(total_vectors)]
    fetch_response = pinecone_index.fetch(ids=vector_ids)
    
    # Fetch all documents from the index with their metadata
    query_response = pinecone_index.query(
        namespace="ns1",
        vector=[0] * 1024,  # Dummy vector to fetch all documents
        top_k=100,  # Increase if you have more documents
        include_values=False,
        include_metadata=True
    )
    
    uploads = []
    if query_response and 'matches' in query_response:
        for match in query_response['matches']:
            metadata = match.metadata
            if metadata:
                uploads.append({
                    'title': metadata.get('title', 'Untitled'),
                    'type': metadata.get('type', 'Document'),
                    'upload_date': metadata.get('upload_date', datetime.now().strftime('%Y-%m-%d'))
                })
    
    return render(request, 'my_uploads.html', {'uploads': uploads})