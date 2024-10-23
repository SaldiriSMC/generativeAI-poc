## Documentation for Wikipedia to Pinecone Database Integration and Chat

### Overview

This project integrates Wikipedia data with a Pinecone vector database and uses Groq cloud for processing user queries. It consists of the following main steps:

1. **Retrieving Wikipedia Content**: Fetch content from Wikipedia pages and save them as text files.
2. **Pinecone Vector Database**: Create a vector database to store embeddings of the Wikipedia content.
3. **Groq API Integration**: Query the vector database and use Groq's model to provide answers based on retrieved context.

---

### Prerequisites

- **Python 3.7+**
- **Pinecone API Key**: You can obtain it by signing up at Pinecone.io.
- **Groq API Key**: Sign up for Groq cloud and obtain the API key.
- **Wikipedia Python Library**: Install via `pip install wikipedia-api`.
- **Dotenv Library**: To load environment variables, install via `pip install python-dotenv`.
- **Pinecone Client**: Install via `pip install pinecone-client`.

---

### Environment Setup

Create a `.env` file in the root directory to store your Pinecone and Groq API keys.

```bash
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
GROQ_API_KEY=your_groq_api_key
```

---

### Project Structure

```bash
.
├── wikipedia_documents_data/    # Folder to store fetched Wikipedia pages
├── wiki_data_collection.py      # Collecting data from Wikipedia
├── vect_db.py                   # File for the integration of Pineoce and CHat using Groq
└── .env                         # Environment variables
```

---

### Detailed Code Breakdown

#### Step 1: Fetch Wikipedia Content

The function `wiki_docs(name)` retrieves content from a specified Wikipedia page, processes potential variations in the name, and stores the text in a local file.

```python
import os
import wikipedia

# Create folder for saving Wikipedia documents
os.makedirs("wikipedia_documents_data", exist_ok=True)

def wiki_docs(name):
    """
    Fetch and store Wikipedia page content.
    """
    try:
        print(f'Topic Name: {name}')
        abc = wikipedia.WikipediaPage(name)
    except:
        # Try multiple name variations in case the original name fails
        abc = wikipedia.WikipediaPage(name.split(" ")[0].lower())
    
    try:
        abc = abc.content
        if abc:
            filename = f"wikipedia_documents_data/{name.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(abc)
        else:
            print(f"Page '{name}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")
```

#### Step 2: Pinecone Vector Database Setup

- **Initiate Pinecone**: Create a connection to Pinecone and initialize the vector database.

```python
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
database_name = os.getenv("PINECONE_INDEX_NAME")

# Create index if it doesn't exist
if database_name not in pc.list_indexes().names():
    pc.create_index(
        name=database_name,
        dimension=1024,
        metric='euclidean',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

pinecone_index = pc.Index(database_name)
```

#### Step 3: Process and Store Data

- **Load Data**: Read the text files containing Wikipedia content and convert them into embeddings for the vector database.

```python
import codecs

# Directory for storing files
directory_path = 'wikipedia_documents_data'
data = []

# Read the text files
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        data.append({'id': filename, 'text': text})

# Generate embeddings using Pinecone inference
embeddings = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[d['text'] for d in data],
    parameters={"input_type": "passage"}
)

# Store the data in the vector database
vectors = []
for d, e in zip(data, embeddings):
    vectors.append({
        "id": d['id'],
        "values": e['values'],
        "metadata": {'text': d['text']}
    })

pinecone_index.upsert(vectors=vectors, namespace="ns1")
```

#### Step 4: Query Processing Using Groq API

- **User Input**: Convert the user's question into a vector and query the vector database to find relevant content.

```python
user_query = input('Write your question here: ')

# Convert user query to embedding
embedding = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[user_query],
    parameters={"input_type": "query"}
)

# Query the database
results = pinecone_index.query(
    namespace="ns1",
    vector=embedding[0].values,
    top_k=3,
    include_values=False,
    include_metadata=True
)

# Extract matched content
matched_info = ' '.join(item['metadata']['text'] for item in results['matches'])
```

#### Step 5: Answer Generation with Groq

- **System Instructions**: Provide the retrieved content as context for Groq to generate an appropriate response.

```python
from groq import Groq

# Connect to Groq API
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# System prompt
context = f"Information: {matched_info}"
sys_prompt = f"""
Instructions:
- You are a knowledgeable assistant...
Context: {context}
"""

# Send query to Groq for processing
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_query}
    ],
    model="llama3-8b-8192"
)

# Output response
print(chat_completion.choices[0].message.content)
```

---

### Usage Instructions

1. **Clone the repository** and set up your environment by installing dependencies using:

    ```bash
    pip install -r requirements.txt
    ```

2. **Add your API keys** in the `.env` file.

3. **Run the script** to fetch Wikipedia data, process it, and query the system:

    ```bash
    python main.py
    ```

4. **Enter your query** when prompted. The system will fetch relevant data from the Wikipedia content and provide a response using Groq's API.

---

### Future Enhancements

- **Error Handling**: Improve error handling for edge cases where Wikipedia data might not be accessible.
- **UI Integration**: Develop a simple web interface to allow users to input queries and receive responses without using the terminal.

---

This setup provides a basic framework for retrieving Wikipedia content, embedding it into a Pinecone vector database, and querying the database using Groq cloud for intelligent answers.