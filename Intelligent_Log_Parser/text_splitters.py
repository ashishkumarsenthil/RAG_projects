from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader 
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil

load_dotenv()
# Set OpenAI API key

openai.api_key = os.environ['OPENAI_API_KEY']

path="./extracted_data/extracted_log_output.txt"

def load_doc(path):
    loader=TextLoader(path, encoding='utf-8')
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Number of chunks created: {len(chunks)}")
    #print(chunks[0].page_content)  # Print the content of the 10th chunk for verification
    return chunks

    
