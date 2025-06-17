from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from text_splitters import split_text
from text_splitters import load_doc

path="./extracted_data/extracted_log_output.txt"
document=load_doc(path)
chunks=split_text(document)
#Document is a class from langchain.schema that represents a page_content and metadata.
def create_vector_store(chunks: list[Document]):
    chunks_page_content = [chunk.page_content for chunk in chunks]
    #print(chunks_page_content) 
    docs = [Document(page_content=chunk) for chunk in chunks_page_content]
    #print(chunks)
    # Initialize OpenAI embeddings and create a vector store using Chroma
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(documents=chunks,embedding=embeddings, collection_name="logs_collection",persist_directory="./chroma_db")
    #print(vector_store)
    # retrieved_docs = vector_store.similarity_search("test", k=5)
    # for i, doc in enumerate(retrieved_docs, 1):
    #     print(f"\n--- Document {i} ---")
    #     print(doc.page_content)
    #return vector_store

#create_vector_store(chunks)
