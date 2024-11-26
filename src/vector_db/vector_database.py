# !pip  install -U docarray
# !pip  install pydantic
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
from tqdm import tqdm
# workspace_path = "./vector_db_v2"
workspace_path= r"vector_db/vectorDB_files_v2"
services_description_file_path="./assets/Services_description_V2.txt"

# Define constants
vector_dimension = 768


# Define the ServiceDoc class
class ServiceDoc(BaseDoc):
    text: str = ''
    embedding: NdArray[vector_dimension]

# Mean Pooling - Takes attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Embedding Model
def embedding_model(doc: str):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')

    # Tokenize the document
    encoded_input = tokenizer(doc, padding=True, truncation=True, return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    doc_embedding = mean_pooling(model_output, encoded_input['attention_mask'])

    # Normalize embeddings
    doc_embedding = F.normalize(doc_embedding, p=2, dim=1)

    return doc_embedding.numpy()[0]

# Push Service Descriptions to the Vector Database
def vector_db_push(service_name:str,service_description:str, workspace: str):
#     doc_embedding = embedding_model(service_description)

    db = HNSWVectorDB[ServiceDoc](workspace=workspace)
    # Index a list of documents with random embeddings
    doc_list = [ServiceDoc(text=service_name, embedding=embedding_model(service_description))]
    db.index(inputs=DocList[ServiceDoc](doc_list))
#     db.index(inputs=DocList[ServiceDoc](record))


# Perform a Similarity Search Query
def vector_search(user_query: str, limit: int):
    db = HNSWVectorDB[ServiceDoc](workspace=workspace_path)
    
    # Generate embedding for the query
    query_embedding = embedding_model(user_query)
    len(query_embedding)
    query_doc = ServiceDoc(text=user_query, embedding=query_embedding)
    
    # Perform a search query
    results = db.search(inputs=DocList[ServiceDoc]([query_doc]), limit=limit)
    
    # Print out the matches
    print(f"Search results for query: '{user_query}'")
    serivces=[]
    for match in results[0].matches:
        print(match.text)
        serivces.append(match.text)
    return serivces

        
def parse_services(file_content):
    services = []
    # Split the content by '---' to separate each service
    service_blocks = file_content.strip().split('---')
    
    for block in service_blocks:
        lines = block.strip().split('\n', 1)  # Split each block into service name and description
        if len(lines) == 2:
            service_name = lines[0].strip()
            service_description = lines[1].strip().replace("\n", "")
            services.append((service_name, service_description))
    
    return services
 

def test_query(query):
    results=vector_search(query, limit=3, workspace=workspace_path)
    print(results)
    return results[0]



# vector_db_push(services=services, workspace=workspace_path)

# [ vector_db_push(service_name=service_name, service_description=service_description,workspace=workspace_path) for service_name,service_description in services]
# Assuming 'services' is a list of tuples containing service_name and service_description
# For example: services = [('service1', 'description1'), ('service2', 'description2'), ...]



def vector_db_push_batch():
    # Load the CSV file to inspect its contents
    workspace_path= r"vectorDB_files_v2"

    with open(services_description_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    services = parse_services(file_content)

        
    # Adding a progress bar to the loop
    [vector_db_push(service_name=service_name, service_description=service_description, workspace=workspace_path) 
    for service_name, service_description in tqdm(services, desc="Pushing to vector DB")]


    print("Service descriptions have been pushed to the vector database.")




# import pandas as pd

# # Load the CSV file to inspect its contents
# ervices_description_file_path = './assets/queries.csv'
# df = pd.read_csv(services_description_file_path)
    


# # Apply the mock LLM function to each row and create a new column 'LLM_Response'
# df['RAG_Response'] = df['Query'].apply(test_query)


