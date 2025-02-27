from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

from datetime import datetime

from vect_db import user_chat_ai, api_keys_gorq_pinecone



@login_required
def get_pinecone_stats(request):
    """
    API View to fetch Pinecone index usage statistics.
    """
    api_keys = request.user.ai_creds.filter(is_active=True).first()
    
    if api_keys:
        pc, database_name, pinecone_index, client = api_keys_gorq_pinecone(
            api_keys.pinecone_api_key,
            api_keys.pinecone_index_name,
            api_keys.groq_api_key
        )
    else:
        pc, database_name, pinecone_index, client = api_keys_gorq_pinecone()

    try:
        stats = pinecone_index.describe_index_stats()
        # Convert NamespaceSummary objects to serializable dictionaries
        namespaces = {}
        for ns_name, ns_data in stats.get("namespaces", {}).items():
            namespaces[ns_name] = {
                "vector_count": getattr(ns_data, "vector_count", 0)
            }

        response_data = {
            "total_vectors": stats.get("total_vector_count", 0),
            "index_fullness": stats.get("index_fullness", 0),
            "namespaces": namespaces,
        }
    except Exception as e:
        response_data = {"error": str(e)}

    return JsonResponse(response_data)


@login_required
def gen_ai_chat(request):
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
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'response': gen_ai_response})
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