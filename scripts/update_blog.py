import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

BLOG_URL = "https://www.monitorenegocios.com.br/blogs/"
OUT = Path("data/posts.json")


class BlogParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.posts = []
        self.current_link = None
        self.current_text = []

        self.meta = {}

    def handle_starttag(self, tag, attrs):

        attrs = dict(attrs)

        if tag == "a":

            href = attrs.get("href", "")

            if "/blogs/post/" in href:

                self.current_link = urljoin(
                    BLOG_URL,
                    href
                )

                self.current_text = []

        if tag == "meta":

            name = (
                attrs.get("property")
                or attrs.get("name")
                or ""
            ).lower()

            content = attrs.get("content", "")

            if name and content:

                self.meta[name] = content

    def handle_data(self, data):

        if self.current_link:

            self.current_text.append(data.strip())

    def handle_endtag(self, tag):

        if tag == "a" and self.current_link:

            title = " ".join(
                x for x in self.current_text
                if x
            ).strip()

            if (
                title
                and self.current_link
                and self.current_link not in [
                    p["url"] for p in self.posts
                ]
            ):

                self.posts.append({
                    "title": title,
                    "url": self.current_link
                })

            self.current_link = None
            self.current_text = []


class ImageParser(HTMLParser):

    def __init__(self):

        super().__init__()

        self.og_image = ""
        self.title = ""

    def handle_starttag(self, tag, attrs):

        attrs = dict(attrs)

        if tag == "meta":

            prop = (
                attrs.get("property")
                or attrs.get("name")
                or ""
            ).lower()

            content = attrs.get("content", "")

            if prop in [
                "og:image",
                "twitter:image"
            ] and content:

                if not self.og_image:

                    self.og_image = content

        if tag == "title":

            self.in_title = True

    def handle_data(self, data):

        if getattr(self, "in_title", False):

            self.title += data

    def handle_endtag(self, tag):

        if tag == "title":

            self.in_title = False


def fetch(url):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0 (compatible; MonitoreBlogBot/1.0)"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return response.read().decode(
            "utf-8",
            errors="ignore"
        )


def get_posts():

    print("Acessando o Blog da Monitore...")

    html = fetch(BLOG_URL)

    parser = BlogParser()

    parser.feed(html)

    return parser.posts[:6]


def get_image(url):

    print("Buscando imagem:", url)

    try:

        html = fetch(url)

        parser = ImageParser()

        parser.feed(html)

        return parser.og_image

    except Exception as error:

        print(
            "Erro ao buscar imagem:",
            error
        )

        return ""


def main():

    posts = get_posts()

    if not posts:

        print(
            "Nenhuma postagem encontrada."
        )

        return

    final_posts = []

    for post in posts:

        image = get_image(
            post["url"]
        )

        final_posts.append({

            "title": post["title"],

            "url": post["url"],

            "date": "",

            "image": image

        })

    OUT.write_text(

        json.dumps(
            final_posts,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"

    )

    print(
        f"{len(final_posts)} "
        "postagens atualizadas."
    )

    for post in final_posts:

        print(
            post["title"]
        )

        print(
            "Imagem:",
            post["image"]
        )


if __name__ == "__main__":

    main()
