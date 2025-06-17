
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain.llms import HuggingFacePipeline
from langchain_community.chat_models import ChatOllama
from transformers import pipeline
import extraction
import text_splitters
import vector_db
import os
import openai 

load_dotenv()
# Set OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

query = input("Enter your query: ")
name_of_file=input("Enter the fileName : ")
html_path = fr"C:\Users\akumarse\Documents\Ashish\RAG_project\data\{name_of_file}.html"

extraction.extract_text_from_html(html_path)

document = text_splitters.load_doc("./extracted_data/extracted_log_output.txt")
chunks = text_splitters.split_text(document)

vector_db.create_vector_store(chunks)


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#Load the document
vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="logs_collection"
)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

relevant_docs = retriever.get_relevant_documents(query)
context = "\n".join([doc.page_content for doc in relevant_docs])

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant named LOG_REVIEWER. Explain the scenario with all keywords inside the testcase and why its failing. If possible try to provide a feedback or solution"),
    ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    # ("system", "If a fail word is encountered, usually its present inside a keyword."),
    # ("system", "This assistant should identify what is the error causing the keywords to fail and give overall failures of the test cases report."),
    # ("system", "Provide a concise and accurate answer based on the context provided."),
])

# #llm = ChatOpenAI()
# llm_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
# llm = HuggingFacePipeline(pipeline=llm_pipeline)
# chain = LLMChain(prompt=chat_prompt, llm=llm)

llm = ChatOllama(model="mistral") 
chain = LLMChain(llm=llm, prompt=chat_prompt)

response = chain.invoke({
    "context": context,
    "question": query
})

print("Answer:", response["text"])
