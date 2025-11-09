#load the documents from docs folder
import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
load_dotenv()

loader = DirectoryLoader("docs", encoding="utf8")
documents = loader.load()

#print the documents
print(documents)

#split the documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

#print the chunks
print(chunks)

#embed the chunks
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
embeddings.embed_documents(chunks)

#print the embeddings using FAISS
faiss = FAISS.from_documents(chunks, embeddings)
print(faiss)

#save the faiss index into faiss_index folder
faiss.save_local("faiss_index")

#load the faiss index
faiss = FAISS.load_local("faiss_index", embeddings)
print(faiss)