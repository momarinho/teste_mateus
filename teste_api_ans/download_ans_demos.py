import argparse
import json
import os
import re
import sys
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
DEFAULT_EXTENSIONS = [
    ".zip",
    ".csv",
    ".xlsx",
    ".xls",
    ".txt",
    ".parquet",
]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = None
        for name, value in attrs:
            if name.lower() == "href":
                href = value
                break
        if href:
            self.links.append(href)


def fetch_html(url, timeout):
    req = Request(url, headers={"User-Agent": "ans-downloader/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def list_links(url, timeout):
    html = fetch_html(url, timeout)
    parser = LinkParser()
    parser.feed(html)
    links = []
    for href in parser.links:
        if href in ("../", "./"):
            continue
        links.append(urljoin(url, href))
    return links


def is_dir_link(url):
    return urlparse(url).path.endswith("/")


def extract_year_from_url(url):
    path = urlparse(url).path
    match = re.search(r"/((19|20)\d{2})/?$", path)
    if match:
        return int(match.group(1))
    return None


def extract_quarter_from_url(url, year_hint=None):
    path = urlparse(url).path
    match = re.search(r"([1-4])T(20\d{2})", path, re.IGNORECASE)
    if match:
        quarter = int(match.group(1))
        year = int(match.group(2))
        return year, quarter
    match = re.search(r"/(20\d{2})/([1-4])T/?", path, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"/(20\d{2})/T([1-4])/?", path, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    if year_hint is not None:
        match = re.search(r"/([1-4])T/?$", path, re.IGNORECASE)
        if match:
            return int(year_hint), int(match.group(1))
        match = re.search(r"/T([1-4])/?$", path, re.IGNORECASE)
        if match:
            return int(year_hint), int(match.group(1))
    return None


def gather_year_urls(base_url, timeout):
    year_urls = {}
    for link in list_links(base_url, timeout):
        year = extract_year_from_url(link)
        if year:
            year_urls[year] = link
    return year_urls


def gather_quarter_entries(base_url, timeout):
    quarter_map = {}
    year_urls = gather_year_urls(base_url, timeout)
    for year, year_url in year_urls.items():
        for link in list_links(year_url, timeout):
            quarter = extract_quarter_from_url(link, year_hint=year)
            if not quarter:
                continue
            quarter_map.setdefault(quarter, []).append(link)
    return quarter_map


def should_download(url, extensions):
    path = urlparse(url).path
    if path.endswith("/"):
        return False
    ext = os.path.splitext(path)[1].lower()
    if ext in (".html", ".htm", ".php", ".asp", ".aspx"):
        return False
    if extensions:
        return ext in extensions
    return True


def collect_files(url, timeout, extensions, max_depth, _depth=0, _seen=None):
    if _seen is None:
        _seen = set()
    if url in _seen:
        return []
    _seen.add(url)

    files = []
    for link in list_links(url, timeout):
        if is_dir_link(link):
            if _depth < max_depth:
                files.extend(
                    collect_files(
                        link,
                        timeout,
                        extensions,
                        max_depth,
                        _depth=_depth + 1,
                        _seen=_seen,
                    )
                )
            continue
        if should_download(link, extensions):
            files.append(link)
    return files


def normalize_local_path(base_url, file_url, output_dir):
    base_path = urlparse(base_url).path
    file_path = urlparse(file_url).path
    if file_path.startswith(base_path):
        rel_path = file_path[len(base_path) :].lstrip("/")
    else:
        rel_path = os.path.basename(file_path)
    return os.path.join(output_dir, *rel_path.split("/"))


def download_file(url, dest, timeout, overwrite, retries, backoff_seconds):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and not overwrite:
        return "skipped", 0, 0, None
    attempts = 0
    while True:
        attempts += 1
        try:
            req = Request(url, headers={"User-Agent": "ans-downloader/1.0"})
            with urlopen(req, timeout=timeout) as resp:
                total = 0
                with open(dest, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 64)
                        if not chunk:
                            break
                        f.write(chunk)
                        total += len(chunk)
            return "downloaded", total, attempts, None
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempts >= retries:
                return "error", 0, attempts, str(exc)
            time.sleep(backoff_seconds * attempts)


def quarter_label(year, quarter):
    return f"{quarter}T{year}"


def main():
    parser = argparse.ArgumentParser(
        description="Baixa as Demonstrações Contábeis mais recentes da ANS."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--output-dir", default=os.path.join("data", "demonstracoes_contabeis")
    )
    parser.add_argument("--quarters", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", default="manifest.json")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--backoff", type=float, default=1.0)
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Lista de extensões permitidas, separadas por vírgula. Use vazio para aceitar qualquer.",
    )
    args = parser.parse_args()

    extensions = [
        ext.strip().lower() for ext in args.extensions.split(",") if ext.strip()
    ]
    if not extensions:
        extensions = None

    quarter_map = gather_quarter_entries(args.base_url, args.timeout)
    if not quarter_map:
        print("Nenhum trimestre encontrado. Verifique o base-url.", file=sys.stderr)
        return 1

    latest_quarters = sorted(quarter_map.keys(), reverse=True)[: args.quarters]
    manifest_entries = []
    summary = {"downloaded": 0, "skipped": 0, "error": 0, "dry-run": 0}

    print(
        "Trimestres selecionados:",
        ", ".join(quarter_label(y, q) for y, q in latest_quarters),
    )

    for year, quarter in latest_quarters:
        entries = quarter_map.get((year, quarter), [])
        if not entries:
            continue
        quarter_files = []
        for entry in entries:
            if is_dir_link(entry):
                quarter_files.extend(
                    collect_files(
                        entry,
                        args.timeout,
                        extensions,
                        args.max_depth,
                    )
                )
            elif should_download(entry, extensions):
                quarter_files.append(entry)

        if not quarter_files:
            print(f"[{quarter_label(year, quarter)}] Nenhum arquivo encontrado.")
            continue

        for file_url in sorted(set(quarter_files)):
            dest = normalize_local_path(args.base_url, file_url, args.output_dir)
            status = "dry-run"
            size = 0
            error = None
            attempts = 0
            try:
                if not args.dry_run:
                    status, size, attempts, error = download_file(
                        file_url,
                        dest,
                        args.timeout,
                        args.overwrite,
                        args.retries,
                        args.backoff,
                    )
            except Exception as exc:
                status = "error"
                error = str(exc)
            manifest_entries.append(
                {
                    "quarter": quarter_label(year, quarter),
                    "url": file_url,
                    "local_path": dest,
                    "status": status,
                    "bytes": size,
                    "error": error,
                    "attempts": attempts,
                }
            )
            summary[status] = summary.get(status, 0) + 1
            print(f"[{quarter_label(year, quarter)}] {status}: {file_url}")

    manifest_path = os.path.join(args.output_dir, args.manifest)
    os.makedirs(args.output_dir, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "base_url": args.base_url,
                "quarters": [quarter_label(y, q) for y, q in latest_quarters],
                "summary": summary,
                "entries": manifest_entries,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print("Manifest salvo em:", manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
