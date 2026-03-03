import os
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def sync_to_notion():
    repo_name = os.getenv("REPO_NAME")
    repo_url = os.getenv("REPO_URL")
    # Получаем теги из GitHub для поля Tech Stack
    topics = os.getenv("REPO_TOPICS", "").split(",")
    
    url = "https://api.notion.com/v1/pages"
    
    # Формируем структуру в точном соответствии с вашим скриншотом
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            # Заголовок страницы
            "Name": {"title": [{"text": {"content": f"Проект: {repo_name}"}}]},
            
            # Ссылка на репозиторий
            "Files & Links": {"url": repo_url},
            
            # Домен (ставим по умолчанию AI/Development или берем из топиков)
            "Domain": {"select": {"name": "AI Development"}},
            
            # Приоритет (Low, как на скрине, или можно настроить логику)
            "Priority": {"select": {"name": "Low"}},
            
            # Статус (In progress, как на скрине)
            "Status": {"status": {"name": "In progress"}},
            
            # Технологический стек (Multi-select)
            "Tech Stack": {
                "multi_select": [{"name": t.strip()} for t in topics if t.strip()]
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"✅ Проект {repo_name} успешно добавлен в портфолио.")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    sync_to_notion()
