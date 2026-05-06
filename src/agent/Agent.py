import re
import json
import AgentState
from ollama import Client
from typing import List, Dict, Any
import requests
import xml.etree.ElementTree as ET

class Agent:
    def __init__(self, prompt):
        self.prompt = prompt
        self.model = "qcwind/qwen3-8b-instruct-Q4-K-M:latest"
        self.client = Client(host="http://localhost:11434")

    def call_model(self):
        response = self.client.generate(
            model=self.model,  
            prompt=self.prompt,
            stream=False,
            options={
                'temperature': 0.9,
                'repeat_penalty': 1.35,
                'repeat_last_n': 128,
                'num_ctx': 2048
            }
        )
        return (response['response'])
    
    def strip_tags(self, text: str) -> str: # Текст, получаемый от Википедии содержал тэги разметки страницы, функция чистит текст от них
        return re.sub(r"<[^>]+>", "", text or "")
    
    def relevance_assessment(self, topic:str, content:list) -> str:
        content = ' '.join(content)
        promt = f'''
        Пользователь ищет информацию по теме "{topic}". 
        Вот что удалось найти по теме: {content}. 
        Оцени, на сколько найденный материал совпадает с заданной темой. 
        Если ты не уверен в том, что текст отвечает заданной тематике, верни только 0.
        Иначе можешь вернуть исходный текст.
        Если ты не уверен в том, что текст отвечает заданной тематике, верни только 0.
        ''' 
        result = self.model_call(promt)
        return result
    
    def wiki_search(self, query:str) -> str:
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
            return []
    
        data = response.json()
        if 'pages' not in data or not data['pages']:
            return []
    
        excerpts = [self.strip_tags(page.get("excerpt", "")) for page in data["pages"]]
        excerpts = self.relevance_assessment(query, excerpts)
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
        query = '+'.join(query.splt())
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
    
print(search_arxiv('gradient boost'))