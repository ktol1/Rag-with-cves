from flask import Flask, request, render_template, session, redirect, url_for
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from markupsafe import Markup
from query_data import query_rag
import re
import requests
import json
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.jinja_env.globals.update(zip=zip, enumerate=enumerate)


def format_result(result):
    """将查询结果格式化为 HTML，将链接转换为超链接"""
    result = result.replace('\n', '<br>')
    result = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', result)
    return result

@app.route('/query', methods=['GET', 'POST'])
def query_page():
    error = None
    if request.method == 'POST':
        query_text = request.form['query']
        if query_text:
            result = query_rag(query_text)  # Assuming query_rag is defined in query_data module
            formatted_result = format_result(result)
            session.setdefault('history', []).append(query_text)
            session.setdefault('results', []).append(formatted_result)
            session.modified = True
            return render_template('query_page.html', result=Markup(formatted_result))
        else:
            error = "Please enter a query."
    return render_template('query_page.html', error=error)

@app.route('/history', methods=['GET'])
def history():
    return render_template('history.html', history=session.get('history', []), results=session.get('results', []))

@app.route('/clear_history', methods=['GET'])
def clear_history():
    session.pop('history', None)
    session.pop('results', None)
    return redirect(url_for('history'))

@app.route('/poc_extractor', methods=['GET', 'POST'])
def poc_extractor():
    if request.method == 'POST':
        text_input = request.form.get('text_input', '')
        if text_input:
            urls = re.findall(r'https?://\S+', text_input)
            results = [fetch_url_content(url) for url in urls]
            print(results)
            processed_results = [invoke_llama(content) for content in results]
            #print(processed_results)
            return render_template('poc_extractor.html', results=processed_results)
        else:
            return render_template('poc_extractor.html', results=["No URL found in input."])
    return render_template('poc_extractor.html')

def fetch_url_content(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url,headers=header)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching URL {url}: {str(e)}"

def invoke_llama(content):
    PROMPT_TEMPLATE = """
    Given the content of a webpage, your task is to analyze and extract critical information. Focus primarily on extracting how to use security vulnerabilities security vulnerabilities and details of the security vulnerabilities. If such details are not available, extract key informational points from the webpage that can be useful for understanding the main topics or issues discussed.

    Webpage Content:
    "{webpage_content}"

    Instructions:
    1. Search through the provided webpage content for how to use security vulnerabilities,give exact steps.
    2. If no security vulnerabilities are present, identify and summarize the Vulnerability Information and Vulnerability Description.

    Please execute these instructions and format the output to highlight the extracted information effectively，please answer me in Chinese.
    """
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(webpage_content=content)
    model = Ollama(model="llama3")
    response_text = model.invoke(prompt)
    return f"Processed content for: {response_text}..."


def invoke_chatgpt(content):
    PROMPT_TEMPLATE = """
    Given the content of a webpage, your task is to analyze and extract critical information. Focus primarily on extracting how to use security vulnerabilities security vulnerabilities and details of the security vulnerabilities. If such details are not available, extract key informational points from the webpage that can be useful for understanding the main topics or issues discussed.

    Webpage Content:
    "{webpage_content}"

    Instructions:
    1. Search through the provided webpage content for how to use security vulnerabilities,give exact steps.
    2. If no security vulnerabilities are present, identify and summarize the Vulnerability Information and Vulnerability Description.

    Please execute these instructions and format the output to highlight the extracted information effectively，please answer me in Chinese.
    """
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(webpage_content=content)
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
        'Authorization': 'Bearer sk-??',
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

@app.route('/openai_query', methods=['GET', 'POST'])
def openai_query():
    if request.method == 'POST':
        user_input = request.form.get('user_input')  # 使用 get 方法避免 KeyError
        if user_input:  # 检查 user_input 是否存在
            response = invoke_openai(user_input)
            print(response)
            return render_template('openai_query.html', response=response, user_input=user_input)
        else:
            return render_template('openai_query.html', error="Please enter some input.")
    return render_template('openai_query.html', response=None)

def invoke_openai(user_input):
    prompt=user_input
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
        'Authorization': 'Bearer sk-??',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return response.json()['choices'][0]['message']['content']

@app.route('/')
def home():
    return redirect(url_for('query_page'))


if __name__ == '__main__':
    app.run(debug=True)
