"""
Module: Vector_Database.py
Author: Moamen Moustafa
Date: 10-4-2023 (during my research internship at IoT Research Lab, Ontario Tech University, Oshawa, ON, Canada)

Description:
This module defines functions for embedding text documents using the "sentence-transformers/all-mpnet-base-v2" model, and for 
interacting with a HNSWVectorDB to push and search for similar documents. It also includes text preprocessing functions such 
as stemming and lemmatization.

Usage:
1. Import the module: `import Vector_Database`
2. Use the provided functions to perform embedding, push documents to the vector database, and search for similar documents.

Example (Pushing a batch of documents to the vector database):
import Vector_Database

txt_file_path = "documents.txt"
workspace = "vector_db_workspace"
vector_search_util.vector_db_push_batch(txt_file_path, workspace)

Note: Make user that documents.txt in the following format
<SERVICE-NAME-1>\n
<SERVICE-DESCRIPTION-PARAGRAPHS-1>\n
<SPLIT using "---">
<SERVICE-NAME-2>\n
<SERVICE-DESCRIPTION-PARAGRAPHS-2>\n
<SPLIT using "---">
...
<SERVICE-NAME-N>\n
<SERVICE-DESCRIPTION-PARAGRAPHS-N>\n
<SPLIT using "---">

Dependencies:
- transformers: Make sure the HuggingFace Transformers library is installed.
- torch: Ensure that PyTorch is installed.
- nltk: Install the NLTK library for stemming (if not already installed).
- spacy: Install the spaCy library with the "en_core_web_lg" model.
- docarray: Install the docarray library for document handling.
- vectordb: Install the vectordb library for vector database operations.
- tqdm: Install tqdm for progress tracking.
"""

from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from nltk.stem import PorterStemmer
import spacy
from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
import time
import warnings
from tqdm import tqdm
# warnings.filterwarnings("ignore")

# Constants
vector_dimension = 768


# Preprocessing
def stem_word(word):
    """
    Perform stemming on a word using the Porter Stemmer.

    Args:
    word (str): The word to be stemmed.

    Returns:
    str: The stemmed word.

    Example:
    ```
    stemmed_word = stem_word("running")
    ```

    """
    stemmer = PorterStemmer()
    return stemmer.stem(word)


def remove_redundant_services_stemming(services):
    """
    Remove redundant services by stemming their names.

    Args:
    services (list of tuple): List of service name and description pairs.

    Returns:
    list of tuple: List of unique service name and description pairs after stemming.

    Example:
    ```
    services = [("run", "Running service"), ("walk", "Walking service")]
    unique_services = remove_redundant_services_stemming(services)
    ```

    """
    stemmed_services = {}
    for service in services:
        service_name, service_description = service
        stemmed_name = stem_word(service_name.lower())
        if stemmed_name not in stemmed_services:
            stemmed_services[stemmed_name] = (
                service_name, service_description)

    return list(stemmed_services.values())


def lemmatize_text(text):
    """
    Perform lemmatization on the input text using spaCy's en_core_web_lg model.

    Args:
    text (str): The input text to be lemmatized.

    Returns:
    str: The lemmatized text.

    Example:
    ```
    lemmatized_text = lemmatize_text("The dogs are barking loudly.")
    ```

    """
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])


def remove_redundant_services_lemmatization(services):
    """
    Remove redundant services by lemmatizing their names.

    Args:
    services (list of tuple): List of service name and description pairs.

    Returns:
    list of tuple: List of unique service name and description pairs after lemmatization.

    Example:
    ```
    services = [("running", "Running service"), ("walks", "Walking service")]
    unique_services = remove_redundant_services_lemmatization(services)
    ```

    """
    lemmatized_services = {}
    for service in services:
        service_name, service_description = service
        lemmatized_name = lemmatize_text(service_name.lower())
        if lemmatized_name not in lemmatized_services:
            lemmatized_services[lemmatized_name] = (
                service_name, service_description)

    return list(lemmatized_services.values())


# Embedding Model
def mean_pooling(model_output, attention_mask):
    """
    Perform mean pooling on the model's output.

    Args:
    model_output (torch.Tensor): The model's output containing token embeddings.
    attention_mask (torch.Tensor): The attention mask.

    Returns:
    torch.Tensor: Mean-pooled embeddings.

    Example:
    ```
    pooled_embeddings = mean_pooling(model_output, attention_mask)
    ```

    """
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(
        -1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def embedding_model(doc: str):
    """
    Embed a text document using the "sentence-transformers/all-mpnet-base-v2" model.

    Args:
    doc (str): The input document to be embedded.

    Returns:
    numpy.ndarray: Document embeddings.

    Example:
    ```
    doc = "This is a sample document."
    embeddings = embedding_model(doc)
     ``
    """

    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained(
        'sentence-transformers/all-mpnet-base-v2')
    model = AutoModel.from_pretrained(
        'sentence-transformers/all-mpnet-base-v2')

    # Tokenize Subservice documents
    encoded_input_docs = tokenizer(
        doc, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_docs_output = model(**encoded_input_docs)

    # Perform pooling
    docs_embeddings = mean_pooling(
        model_docs_output, encoded_input_docs['attention_mask'])

    # Normalize embeddings
    docs_embeddings = F.normalize(docs_embeddings, p=2, dim=1)

    return docs_embeddings.numpy()


# # Vector Database
# # Init. specifc datatype for vector database
class ToDoc(BaseDoc):
    text: str = ""
    embedding: NdArray[vector_dimension]


def vector_db_push(doc: tuple, workspace: str):
    """
    Push a document to the HNSWVectorDB.

    Args:
    doc (tuple): A tuple containing a document name and content.
    workspace (str): The directory path for the vector database workspace.

    Example:
    ```
    document = ("Document 1", "This is the content of document 1.")
    vector_db_push(document, "vector_db_workspace")
    ```

    """
    doc_embedding = embedding_model(doc=doc[1])[0]
    doc_name = doc[0]

    db = HNSWVectorDB[ToDoc](workspace=f'./{workspace}')
    record = [ToDoc(text=doc_name, embedding=doc_embedding)]
    db.index(inputs=DocList[ToDoc](record))


def vector_db_push_batch(txt_file_path: str, workspace: str):
    """
    Push a batch of documents from a text file to the vector database.

    Args:
    txt_file_path (str): The path to the text file containing documents.
    workspace (str): The directory path for the vector database workspace.

    Example:
    ```
    txt_file_path = "documents.txt"
    workspace = "vector_db_workspace"
    vector_db_push_batch(txt_file_path, workspace)
    ```

    (Please read the example in the begining for the file.)

    """
    try:
        print("gett in")
        # file processing.
        with open(txt_file_path, "r", encoding='latin-1') as file:
            content = file.read()

        paragraphs = content.split("---\n")

        services = []
        temp_list = []
        for paragraph in paragraphs:
            lines = paragraph.strip().split('\n')
            service_name = lines[0].strip().encode('latin1').decode('utf-8')

            if service_name not in temp_list and service_name != "":

                temp_list.append(service_name)
                service_description = ' '.join(lines[1:]).strip()

                services.append((service_name, service_description))
        print("File Processing Done")
        services = remove_redundant_services_stemming(services=services)
        print("Stemming Done")

        for i in tqdm(range(0, len(services)), desc=f"Pushing to {workspace} "):
            vector_db_push(doc=services[i], workspace=workspace)
            time.sleep(0.1)

        print("Successful Insert!")

    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")


def vector_search(user_query: str, limit: int):
    """
    Search for similar documents in the HNSWVectorDB based on a user query.

    Args:
    user_query (str): The user's query text.
    limit (int): The maximum number of similar documents to retrieve.
    workspace (str): The directory path for the vector database workspace.

    Returns:
    list: A list of similar documents based on the user query.

    Example:
    ```
    query = "Search for relevant documents."
    limit = 5
    results = vector_search(query, limit, "vector_db_workspace")
    ```

    """
    workspace= r"vector_db/vectorDB_files"
    db = HNSWVectorDB[ToDoc](workspace=workspace)
    # Perform a search query
    query = ToDoc(text=user_query, embedding=embedding_model(doc=user_query))
    results = db.search(inputs=DocList[ToDoc]([query]), limit=limit)
    # Print out the matches
    return results[0].matches.text[:limit]


# vector_db_push_batch(
#     "./Vector Database Utils/Services_description.txt", "Services Vector Database")

# results= vector_search(user_query= "I want to drink coffee", limit= 3)
# print(results)

# vector_db_push_batch("./assets/Services_description_V2.txt", "vectorDB_files")