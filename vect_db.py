import os
import time

from dotenv import load_dotenv
from groq import Groq
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Initiate Pinecone Database
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

# Vector Database Name
database_name = os.getenv("PINECONE_INDEX_NAME")

# connect to vector database
pinecone_index = pc.Index(database_name)


def vec_db_data_transfer(file_name, file_content):
    # If database is not available than create it
    if database_name not in pc.list_indexes().names():
        pc.create_index(
            name=database_name,
            dimension=1024,
            metric='euclidean',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )

    # Directory path to you data files
    directory_path = 'wikipedia_documents_data'

    # Convert product data into proper array for later to convert them to vector data,
    # in this for id is the filename and text is the content of the file
    data = [
        {
            'id': file_name,
            'text': file_content,
        }
    ]

    # for filename in os.listdir(directory_path):
    # file_path = os.path.join(directory_path, filename)
    # with codecs.open(file_path, 'r', encoding='utf-8') as f:
    #     text = f.read()
    #     data.append({'id': filename, 'text': text})

    # Convert data into embeddings
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[d['text'] for d in data],
        parameters={"input_type": "passage", "truncate": "END"}
    )

    # Wait for the index to be ready
    while not pc.describe_index(database_name).status['ready']:
        time.sleep(1)

    # Format id - Filename, values - vector data, and metadat - metadata from file to send to vector database
    vectors = []
    for d, e in zip(data, embeddings):
        vectors.append({
            "id": d['id'],
            "values": e['values'],
            "metadata": {'text': d['text']}
        })

    # Pass data to vector database
    pinecone_index.upsert(
        vectors=vectors,
        namespace="ns1"
    )

    return True


def user_chat_ai(user_query):
    """

    :param user_query:
    :return:
    """
    # Convert user query into vector format
    embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[user_query],
        parameters={
            "input_type": "query"
        }
    )

    # Query vector database on the base of user input vector
    results = pinecone_index.query(
        namespace="ns1",
        vector=embedding[0].values,
        top_k=3,
        include_values=False,
        include_metadata=True
    )

    # Vector database returned results on the base of user query
    matched_info = ' '.join(item['metadata']['text'] for item in results['matches'])

    # system prompt to provide answers on the base of returned results of database
    context = f"Information: {matched_info}"
    sys_prompt = f"""
    Instructions:
    - You are a knowledgeable assistant. Only provide data based on your knowledge in this role.
    - Be helpful and answer questions concisely. If you don't know the answer, say 'I don't know'
    - Utilize the context provided for accurate and specific information.
    Context: {context}
    """

    # initial Groq connection
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY'),
    )

    # Add Prompt to user query
    user_query_with_instruction = (
            "Important Note: Only provide data from the role 'system'. "
            "Your response should only contain exact words and sentences from the system role content. "
            "Now, answer this: " + user_query
    )

    # Chat with groq API on the base of our text file
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",  # Role of the system message
                "content": sys_prompt,  # System prompt content
            },
            {
                "role": "user",  # Role of the user
                "content": user_query_with_instruction,  # User prompt input
            }
        ],
        model="llama3-8b-8192",  # Specify the model name
    )

    # Print the response content
    return chat_completion.choices[0].message.content
    # return chat_completion

# # User Question
# user_message = str(input('Write your question here: '))
# ai_response = user_chat_ai(user_message)
# print(ai_response)
# vec_db_data_transfer()
