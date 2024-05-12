from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_openai import OpenAIEmbeddings
import os
os.environ["OPENAI_API_BASE"] = "https://api.chatanywhere.tech/v1"
os.environ["OPENAI_API_KEY"] = "sk-??"
# def get_embedding_function():
#     embeddings = OllamaEmbeddings(model="llama3")
#     # embeddings = OllamaEmbeddings(model="nomic-embed-text")
#     return embeddings
import openai
def get_embedding_function():
    return OpenAIEmbeddings()

