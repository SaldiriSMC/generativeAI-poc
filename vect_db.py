import os
import time
import magic
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from groq import Groq

load_dotenv()

def api_keys_gorq_pinecone(pinecone_api_key, pinecone_index_name, groq_api_key):
    try:
        pc = Pinecone(api_key=str(pinecone_api_key))
        
        database_name = str(pinecone_index_name)
        existing_indexes = [index['name'] for index in pc.list_indexes()]
        
        if database_name not in existing_indexes:
            pc.create_index(
                name=database_name,
                dimension=1024,
                metric='euclidean',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        else:
            print(f"[INFO] Index '{database_name}' already exists.")
        
        # Ensure index is ready
        while not pc.describe_index(database_name).status['ready']:
            time.sleep(2)

        pinecone_index = pc.Index(database_name)
        client = Groq(api_key=str(groq_api_key))
        
        return pc, database_name, pinecone_index, client

    except Exception as e:
        return None, None, None, None


def vec_db_data_transfer(file_name=None, file_content=None, pc=None, database_name=None, pinecone_index=None):
    try:
        if not file_name or not file_content:
            return False


        # Check if the database exists in Pinecone
        existing_indexes = [index['name'] for index in pc.list_indexes()]
        if database_name not in existing_indexes:
            pc.create_index(
                name=database_name,
                dimension=1024,
                metric='euclidean',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        else:
            print(f"[INFO] Pinecone index '{database_name}' exists.")

        # Ensure index is ready
        while not pc.describe_index(database_name).status['ready']:
            time.sleep(2)

        # Validate file encoding
        if isinstance(file_content, bytes):
            try:
                file_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                return False

        # Generate embeddings
        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[file_content],
            parameters={"input_type": "passage", "truncate": "END"}
        )

        if not embeddings or 'values' not in embeddings[0]:
            return False

        # Format vectors
        vectors = [{
            "id": file_name,
            "values": embeddings[0]['values'],
            "metadata": {
                'text': file_content,
                'title': os.path.basename(file_name),
                'type': magic.from_buffer(file_content.encode(), mime=True),
                'upload_date': time.strftime('%Y-%m-%d')
            }
        }]

        response = pinecone_index.upsert(vectors=vectors, namespace="ns1")

        return True

    except Exception as e:
        return False



def user_chat_ai(user_query, pc, pinecone_index, client):
    """ Query Pinecone and generate AI response. """

    # Convert user query into a vector format
    embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[user_query],
        parameters={"input_type": "query"}
    )

    # Query Pinecone to find matching documents
    results = pinecone_index.query(
        namespace="ns1",  # Ensure you're using the right namespace
        vector=embedding[0]['values'],
        top_k=3,  # Increase top_k to get more results
        include_values=False,
        include_metadata=True
    )

    if 'matches' not in results or len(results['matches']) == 0:
        print("[WARNING] No matching results found in Pinecone!")
        return "No relevant information found in the database."

    # Extract matched results
    matched_info = ' '.join(item['metadata']['text'] for item in results['matches'])

    # If there are no matches, return an error message
    if not matched_info:
        return "I couldn't find any relevant information in my database."

    # Generate AI response using Groq API
    sys_prompt = f"""
    Instructions:
    - You are an AI assistant. Answer questions only using the given context.
    - If the context is empty, say 'I don't know the answer'.
    Context: {matched_info}
    """

    user_prompt = f"Important Note: Only respond based on the provided context.\nUser: {user_query}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3-8b-8192"
        )

        ai_response = chat_completion.choices[0].message.content
        return ai_response

    except Exception as e:
        return "There was an error processing your request."