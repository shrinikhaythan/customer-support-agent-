from langchain_core.documents import Document 
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter 
import os 
embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter= RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=200,add_start_index=True)
folder_path="/Users/pakshirajdeivanayagam/Desktop/customer-support-agent-/customer-support-agent-/knowledge base"
file_names=["company_policy.txt","faq.txt","pricing_guide.txt","technical_manual.txt"]
final_chunks=[]
for  name in file_names :
    final_chunk=[]
    file_path=os.path.join(folder_path,name)
    with open (file_path,'r',encoding="utf-8") as f1 :
        f=f1.read()
        l=name.split('.')
        metadata={"source":l[0]}
       
        chunks=text_splitter.create_documents(
            texts=[f],metadatas=[metadata]
        )
        final_chunks.extend(chunks)

vector_db=FAISS.from_documents(final_chunks,embeddings)

vector_db.save_local("vector_database")


       




