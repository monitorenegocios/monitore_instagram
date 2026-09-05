import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urljoin
from datetime import datetime

RSS_URL = "https://www.monitorenegocios.com.br/blogs/feed"
OUTPUT_FILE = "data/posts.json"
MAX_POSTS = 6


def get_image_from_rss(item):
    """Tenta encontrar uma imagem diretamente no RSS."""
    for element in item.iter():
        tag = element.tag.lower()

        if "image" in tag:
            url = element.attrib.get("url")
            if url:
                return url.strip()

            if element.text and element.text.strip().startswith("http"):
                return element.text.strip()

        if tag.endswith("enclosure"):
            url = element.attrib.get("url")
            if url:
                return url.strip()

    return ""


def get_image_from_page(url):
    """Busca a imagem de capa do artigo através de og:image."""
    if not url:
        return ""

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']'
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)

            if match:
                image_url = unescape(match.group(1).strip())
                return urljoin(url, image_url)

    except Exception as error:
        print(f"Não foi possível obter a imagem de {url}: {error}")

    return ""


def get_image(item, url):
    """Primeiro tenta o RSS. Se não encontrar, busca a capa do artigo."""
    image = get_image_from_rss(item)

    if image:
        return image

    print(f"Imagem não encontrada no RSS. Buscando capa da página: {url}")

    return get_image_from_page(url)


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

    print("Acessando RSS do Zoho...")

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

        image = get_image(item, url)

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
