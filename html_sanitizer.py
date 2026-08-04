from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse


ALLOWED_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "div",
    "em",
    "figcaption",
    "figure",
    "h2",
    "h3",
    "h4",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "span",
    "strong",
    "u",
    "ul",
}
VOID_TAGS = {"br", "hr", "img"}
DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed"}
ALLOWED_IMAGE_DATA_PREFIXES = (
    "data:image/png;",
    "data:image/jpeg;",
    "data:image/webp;",
)


def safe_url(value, allow_data_image=False):
    text = str(value or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    if allow_data_image and lowered.startswith(ALLOWED_IMAGE_DATA_PREFIXES):
        return text
    if text.startswith("/"):
        return text
    scheme = urlparse(text).scheme.lower()
    if scheme in {"http", "https", "mailto", "tel"}:
        return text
    return ""


class RichHtmlSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.drop_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth:
            return
        if tag not in ALLOWED_TAGS:
            return

        clean_attrs = []
        for name, value in attrs:
            name = str(name or "").lower()
            value = str(value or "")
            if name.startswith("on") or name == "style":
                continue
            if tag == "a" and name == "href":
                href = safe_url(value)
                if href:
                    clean_attrs.append(("href", href))
                    clean_attrs.append(("target", "_blank"))
                    clean_attrs.append(("rel", "noopener"))
                continue
            if tag == "img" and name == "src":
                src = safe_url(value, allow_data_image=True)
                if src:
                    clean_attrs.append(("src", src))
                continue
            if tag == "img" and name == "alt":
                clean_attrs.append(("alt", value))
                continue
            if name == "class":
                clean_attrs.append(("class", value))
                continue
        attr_text = "".join(f' {name}="{escape(value, quote=True)}"' for name, value in clean_attrs)
        self.parts.append(f"<{tag}{attr_text}>")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            if self.drop_depth:
                self.drop_depth -= 1
            return
        if self.drop_depth:
            return
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.drop_depth:
            self.parts.append(escape(data, quote=False))

    def handle_entityref(self, name):
        if not self.drop_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name):
        if not self.drop_depth:
            self.parts.append(f"&#{name};")


def sanitize_rich_html(html):
    parser = RichHtmlSanitizer()
    parser.feed(str(html or ""))
    parser.close()
    return "".join(parser.parts).strip()
