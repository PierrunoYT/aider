import re
from pathlib import Path
from urllib.parse import urlsplit

from patch import urls


def test_urls():
    root = Path(__file__).resolve().parents[2]
    for name, url in vars(urls).items():
        if name.startswith("_"):
            continue
        parsed = urlsplit(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == "github.com"
        if url.startswith(urls.docs):
            relative = parsed.path.removeprefix("/PierrunoYT/patch/blob/main/")
            target = root / relative
            assert target.exists(), url
            if parsed.fragment:
                headings = re.findall(r"^#+ (.+)$", target.read_text(), re.MULTILINE)
                anchors = {heading.lower().replace(" ", "-") for heading in headings}
                assert parsed.fragment in anchors, url


def test_packaged_documentation_links():
    root = Path(__file__).resolve().parents[2]
    for file in (root / "patch/docs").glob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            parsed = urlsplit(link)
            if parsed.scheme:
                continue
            target = file.parent / parsed.path
            assert target.exists(), (file, link)
            if parsed.fragment:
                headings = re.findall(r"^#+ (.+)$", target.read_text(), re.MULTILINE)
                assert parsed.fragment in {h.lower().replace(" ", "-") for h in headings}
