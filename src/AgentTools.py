import re
import json
from ollama import Client
from typing import List, Dict, Any
import requests
import xml.etree.ElementTree as ET
from .CastomErr import *


def call_model(client, model:str, prompt:str):
    response = client.generate(
        model=model,  
        prompt=prompt,
        stream=False,
        options={
            'temperature': 0.9,
            'repeat_penalty': 1.35,
            'repeat_last_n': 128,
            'num_ctx': 2048
        }
    )
    return (response['response'])
    
def extract_topic(client, model, prompt:str) -> str: 
    prompt = f''' 
    Пользователь ввел следующий запрос: "{prompt}"
    На основе этого запроса сформулируй тему, которую пользователь хочет изучить.
    Если пользователь прямо не указал, что он конкретно хочет найти, или не может сформулировать тему, постарайся помочь пользователю сформулировать тему правильно.
    Если пользователь конкретно указал, какую тему ищет, или ты смог сформулировать тему, то ответь только названием темы.
    Если не удалось сформулировать тему, или нельзя уверенно сказать, что имел в виду пользователь, верни только 0.
    Если пользователь задал тему и в ней есть орфографические ошибки или опечатки - исправь их.
    При формировании темы соблюдай следующие правила:
    - тема формируется только на английском языке
    - страйся формулировать тему кратко, в двух-трех словах
    - тема формируется для дальнейшего поиска статей
     '''

    response = call_model(client, model, prompt)
    if response == '0':
        raise CustomErr('Не удалось определить тему запроса \U0001F625')
    return (response)
    
def strip_tags(text: str) -> str: # Текст, получаемый от Википедии содержал тэги разметки страницы, функция чистит текст от них
    return re.sub(r"<[^>]+>", "", text or "")
    
def relevance_assessment(client, model:str, topic:str, content:list) -> str:
    content = ' '.join(content)
    prompt = f'''
    Пользователь ищет информацию по теме "{topic}". 
    Вот что удалось найти по теме: {content}. 
    Оцени, на сколько найденный материал совпадает с заданной темой. 
    Если ты не уверен в том, что текст отвечает заданной тематике, верни только 0.
    Иначе можешь вернуть исходный текст.
    Если ты не уверен в том, что текст отвечает заданной тематике, верни только 0.
    ''' 
    result = call_model(client, model, prompt)
    return result
    
def wiki_search(client, model:str, query:str) -> str:
    url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
    params = {
        'q': query,
        'limit': 10  
    }
    headers = {
        "User-Agent": "my-local-tool/0.1 (personal non-commercial project; email: rekjs2llb@mozmail.com)", # Для корректной работы необходимо указать свой почтовый адресс, без этого блокируется доступ
        "Accept": "application/json"}
    response = requests.get(url, params=params, headers=headers, timeout=30)
    
    if response.status_code != 200: # Проверка, получили ли мы текст по запросу. Если нет, возвращает пустой список
        raise HTTPError(response.status_code, f"HTTP error occurred: {response.status_code} - {response.text}")
    
    data = response.json()
    if 'pages' not in data or not data['pages']:
        return []
    
    excerpts = [strip_tags(page.get("excerpt", "")) for page in data["pages"]]
    excerpts = relevance_assessment(client, model, query, excerpts)
    if excerpts == '0':
         return []
    
    return excerpts
    
def search_openalex(query: str, per_page: int = 5) -> List[dict]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,display_name,publication_year,abstract_inverted_index,authorships"
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["results"]
    
def invert_abstract(inv_idx: dict) -> str:
    if not inv_idx:
        return ""
    words = []
    for token, positions in inv_idx.items():
        for pos in positions:
            words.append((pos, token))
    words.sort(key=lambda x: x[0])
    return " ".join(token for _, token in words)
    
def search_arxiv(query:str, per_page: int=5) -> str:
    query = '%20'.join(query.split())
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={per_page}'
    response = requests.get(url, timeout=30).text
    root = ET.fromstring(response)
    result = []
    for elem in root.iter():
        if elem.tag =="{http://www.w3.org/2005/Atom}id":
            result.append(f"id: {elem.text}")
        if elem.tag =="{http://www.w3.org/2005/Atom}title":
            result.append(f"title: {elem.text}")       
        if elem.tag =="{http://www.w3.org/2005/Atom}sumary":
            result.append(f"sumary: {elem.text}")  
        if elem.tag =="{http://www.w3.org/2005/Atom}published":
            result.append(f"published: {elem.text}")  
        if elem.tag =="{http://www.w3.org/2005/Atom}name":
            result.append(f"name: {elem.text}")  
    return ' '.join(result[2::])
    