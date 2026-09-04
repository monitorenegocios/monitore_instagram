import json
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from datetime import datetime

RSS_URL = "https://www.monitorenegocios.com.br/blog-feed.xml"
OUTPUT_FILE = "data/posts.json"
MAX_POSTS = 6


def get_image(item):
    # Tenta encontrar imagem no RSS
    for element in item.iter():
        tag = element.tag.lower()

        if "image" in tag:
            url = element.attrib.get("url")
            if url:
                return url

            if element.text and element.text.startswith("http"):
                return element.text.strip()

        if tag.endswith("enclosure"):
            url = element.attrib.get("url")
            if url:
                return url

    return ""


def clean_date(date_text):
    if not date_text:
        return ""

    try:
        parsed = datetime.strptime(
            date_text[:25],
            "%a, %d %b %Y %H:%M:%S"
        )
        return parsed.strftime("%d.%m.%y")
    except Exception:
        return date_text


def main():

    print("Acessando RSS do Wix...")

    request = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read()

    print("RSS acessado com sucesso.")

    root = ET.fromstring(xml_data)

    posts = []

    for item in root.findall(".//item")[:MAX_POSTS]:

        title_element = item.find("title")
        link_element = item.find("link")
        date_element = item.find("pubDate")

        title = (
            unescape(title_element.text.strip())
            if title_element is not None and title_element.text
            else ""
        )

        url = (
            link_element.text.strip()
            if link_element is not None and link_element.text
            else ""
        )

        date = (
            clean_date(date_element.text.strip())
            if date_element is not None and date_element.text
            else ""
        )

        image = get_image(item)

        posts.append({
            "title": title,
            "url": url,
            "date": date,
            "image": image
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            posts,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"{len(posts)} posts atualizados.")
    print(f"Arquivo atualizado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
