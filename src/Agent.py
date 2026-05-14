from .AgentTools import *
from  .AgentState import AgentState
from .CastomErr import *
from ollama import Client


class Agent:
    def __init__(self):
        self.model = "qcwind/qwen3-8b-instruct-Q4-K-M:latest"
        self.client = Client(host="http://localhost:11434")
        
    def run(self, prompt:str) -> str:
        try:
            topic = extract_topic(self.client, self.model, prompt)
            wiki_context = wiki_search(self.client, self.model, topic)
            papers = search_openalex(topic, per_page=5)
            notes = []
            for paper in papers:
                abstract = invert_abstract(paper.get("abstract_inverted_index"))
                authors = [authorship['author']['display_name'] for authorship in paper.get("authorships", [])]
                notes.append({
                    'title': paper.get("display_name", ""),
                    'year': paper.get("publication_year", ""),
                    'authorships': authors,
                    'abstract': abstract
                    })
            request = f'''
                Подготовь научно-аналитический обзор по теме: {topic}
                Общий контекст:
                {wiki_context}
                Источники:
                {json.dumps(notes, ensure_ascii=False)}
                Обязательная структура:
                - определение
                - основные подходы
                - 3-5 ключевых работ
                - применения
                - ограничения
            '''
            response = call_model(self.client, self.model, request)
            response += '\n### Использованные источники'
            for i, paper in enumerate(notes, 1):
                response += f"\n{i}. {paper['title']}. {', '.join(paper['authorships'])}, {paper['year']}"

            return response
        except CustomErr as err:
            return err.message
        except HTTPError as err:
            return f"Не удалось получить ответ от Wikipedia. Код ошибки: {err.status_code} \U0001F625"
