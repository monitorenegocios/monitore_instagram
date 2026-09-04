import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from email.utils import parsedate_to_datetime

RSS = "https://www.monitorenegocios.com.br/blog-feed.xml"
OUT = Path("data/posts.json")

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "media": "http://search.yahoo.com/mrss/"
}


def text(element, name):
    item = element.find(name)

    if item is not None and item.text:
        return item.text.strip()

    return ""


def first_image(item):
    # Procura imagem em media:content
    for tag in ["media:content", "media:thumbnail"]:
        element = item.find(tag, NS)

        if element is not None:
            url = (
                element.attrib.get("url")
                or element.attrib.get("href")
            )

            if url and url.startswith("http"):
                return url

    # Procura imagem em enclosure
    enclosure = item.find("enclosure")

    if enclosure is not None:
        url = enclosure.attrib.get("url")

        if url and url.startswith("http"):
            return url

    # Procura imagem dentro do conteúdo do artigo
    encoded = item.find("content:encoded", NS)

    if encoded is not None and encoded.text:
        html = encoded.text

        match = re.search(
            r'<img[^>]+(?:src|data-src)=["\']([^"\']+)',
            html,
            re.IGNORECASE
        )

        if match:
            return unescape(match.group(1))

    # Procura imagem na descrição
    description = text(item, "description")

    match = re.search(
        r'<img[^>]+(?:src|data-src)=["\']([^"\']+)',
        description,
        re.IGNORECASE
    )

    if match:
        return unescape(match.group(1))

    return ""


def main():

    request = urllib.request.Request(
        RSS,
        headers={
            "User-Agent": "Mozilla/5.0 Monitore Blog Updater"
        }
    )

    try:

        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()

    except Exception as error:

        print("Erro ao acessar o RSS:", error)
        return

    try:

        root = ET.fromstring(data)

    except Exception as error:

        print("Erro ao interpretar RSS:", error)
        return

    items = root.findall(".//item")

    posts = []

    for item in items[:6]:

        title = text(item, "title")
        link = text(item, "link")
        pub_date = text(item, "pubDate")

        date = ""

        if pub_date:

            try:

                date = parsedate_to_datetime(
                    pub_date
                ).strftime("%d.%m.%y")

            except Exception:

                date = pub_date[:10]

        if title and link:

            posts.append({
                "title": title,
                "url": link,
                "date": date,
                "image": first_image(item)
            })

    if posts:

        OUT.write_text(
            json.dumps(
                posts,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(
            f"{len(posts)} publicações atualizadas."
        )

    else:

        print(
            "Nenhuma publicação encontrada. "
            "O arquivo atual foi mantido."
        )


if __name__ == "__main__":
    main()
