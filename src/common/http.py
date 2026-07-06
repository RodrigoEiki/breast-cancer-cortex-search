from urllib.request import Request, urlopen


USER_AGENT = "breast-cancer-cortex-search/0.1 contact=local-research"


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(req, timeout=45) as response:
        return response.read()

