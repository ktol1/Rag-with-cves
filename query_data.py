import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import requests
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are an assisant of network security.Given the context provided below, answer the corresponding question, provide details of CVEs if available for CVEs mentioned, and offer suggestions related to the vulnerability.

Context:
{context}

Question:
{question}

Instructions:
1. Answer the question based solely on the provided context.
2. If the context mentions any CVEs (Common Vulnerabilities and Exposures), provide the POC details or the URL of github available and show the source of cve.
3. Offer practical suggestions to address the vulnerability described in the context.

"""



def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

def invoke_chatgpt(prompt):
    import requests
    import json
    print(prompt)
    url = "https://api.chatanywhere.tech/v1/chat/completions"
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'Authorization': 'Bearer sk-z81ouDI5vT409mNv5n7r9YCVLuVlBAKR0ZqBExizaoSw9hxj',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    #print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()  # 解析 JSON 数据
    if 'choices' in response_data and len(response_data['choices']) > 0:
        # 获取第一个 choice 中的 message 的 content
        message_content = response_data['choices'][0]['message']['content']
        return message_content.strip()  # 返回处理过的字符串，移除前后空白字符
    else:
        return response.text  # 没有找到有效响应时返回的默认消息

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB. k的数量表示的是索要查询的值词嵌入最接近的k个文档快
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    #print(prompt)

    #model = Ollama(model="llama3")
    #response_text = model.invoke(prompt)
    response_text=invoke_chatgpt(prompt)


    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return formatted_response


if __name__ == "__main__":
    main()
