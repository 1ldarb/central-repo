import os
import requests
import sys

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def is_already_in_notion(repo_url: str) -> bool:
    """Проверяем, не добавлен ли проект уже в базу Notion (по URL)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    data = {
        "filter": {
            "property": "Files & Links",
            "url": {"equals": repo_url}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        results = response.json().get("results", [])
        return len(results) > 0
    return False


def sync_to_notion():
    repo_name = os.getenv("REPO_NAME", "")
    repo_url = os.getenv("REPO_URL", "")
    repo_description = os.getenv("REPO_DESCRIPTION", "") or ""
    topics_raw = os.getenv("REPO_TOPICS", "")
    topics = [t.strip() for t in topics_raw.split(",") if t.strip()]

    if not repo_name or not repo_url:
        print("❌ REPO_NAME или REPO_URL не заданы.")
        sys.exit(1)

    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ NOTION_TOKEN или DATABASE_ID не заданы.")
        sys.exit(1)

    # Проверка на дубликат
    if is_already_in_notion(repo_url):
        print(f"⚠️  Проект «{repo_name}» уже есть в Notion. Пропускаем.")
        sys.exit(0)

    url = "https://api.notion.com/v1/pages"

    properties = {
        # Заголовок страницы
        "Name": {
            "title": [{"text": {"content": repo_name}}]
        },
        # Ссылка на репозиторий
        "Files & Links": {
            "url": repo_url
        },
        # Статус
        "Status": {
            "status": {"name": "In progress"}
        },
        # Приоритет
        "Priority": {
            "select": {"name": "Low"}
        },
        # Домен
        "Domain": {
            "select": {"name": "AI Development"}
        },
    }

    # Tech Stack добавляем только если есть топики
    if topics:
        properties["Tech Stack"] = {
            "multi_select": [{"name": t} for t in topics]
        }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
    }

    # Добавляем описание как блок, если оно есть
    if repo_description:
        data["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": repo_description}}]
                }
            }
        ]

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"✅ Проект «{repo_name}» успешно добавлен в портфолио Notion!")
    else:
        print(f"❌ Ошибка {response.status_code}:")
        print(response.text)
        sys.exit(1)


if __name__ == "__main__":
    sync_to_notion()
