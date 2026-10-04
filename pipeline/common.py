"""Shared helpers for the slice pipeline: paths, cached HTTP, TSV output and the 14-column edge format of data/atlas."""
import csv, datetime, gzip, hashlib, json, os, re, time, urllib.parse, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ATLAS = os.path.join(ROOT, "data", "atlas")
SLICE = os.path.join(ROOT, "data", "slice")
CACHE = os.path.join(SLICE, "cache")
EDGE_COLS = ["edge_id", "subject", "predicate", "object", "source", "source_id", "source_url", "retrieved_date", "evidence_type",
             "evidence_code", "confidence", "quote", "contradicted_by", "attributes"]
EVIDENCE_TYPES = ("observed", "extracted", "inferred")
_last = {}


def today():
    return datetime.date.today().isoformat()


def cached(source, key, url, data=None, headers=None, min_interval=0.4, ok=None):
    """Fetch url once and keep the response under data/slice/cache/<source>/, so a rebuild runs offline.

    Returns (payload, retrieved_date). JSON responses are parsed; anything else comes back as text.
    A payload failing ok(payload) is not cached and raises ValueError.
    """
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", key)[:80] + "-" + hashlib.sha1((url + json.dumps(data)).encode()).hexdigest()[:8]
    path = os.path.join(CACHE, source, safe + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        return c["payload"], c["retrieved"]
    wait = min_interval - (time.time() - _last.get(source, 0))
    if wait > 0:
        time.sleep(wait)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": "raraction-atlas/0.1", **({"Content-Type": "application/json"} if body else {}), **(headers or {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode("utf-8")
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    _last[source] = time.time()
    try:
        payload = json.loads(text)
    except ValueError:
        payload = text
    if ok and not ok(payload):
        raise ValueError(f"{source} {key}: {str(payload)[:200]}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "request": data, "retrieved": today(), "payload": payload}, f, ensure_ascii=False)
    return payload, today()


def url(base, **params):
    return base + "?" + urllib.parse.urlencode(params)


def read_tsv(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(cols)
        w.writerows(rows)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def person_id(last, first):
    """Surname plus full first name. Sources disagree on middle names and initials, so only the first given name is kept;
    a surname with an initial alone is too common to merge people safely."""
    first = norm(first).split()
    if not last or not first or len(first[0]) < 2:
        return None
    return "PERSON:" + norm(last).replace(" ", "-") + "_" + first[0]


def split_name(full):
    """'Matthijs Verhage, MD, PhD' -> ('Verhage', 'Matthijs')."""
    full = re.sub(r",.*$|\b(Dr|Prof|MD|PhD|MSc|Professor)\b\.?", "", full).strip()
    parts = full.split()
    return (parts[-1], parts[0]) if len(parts) >= 2 else (None, None)


def load_slice():
    with open(os.path.join(SLICE, "slice.json"), encoding="utf-8") as f:
        return json.load(f)


class Graph:
    """Collects nodes and edges for one source and writes them as <name>_nodes.tsv and <name>_edges.tsv in data/slice/parts."""

    def __init__(self, name):
        self.name, self.nodes, self.edges = name, {}, []

    def node(self, nid, ntype, name, **attrs):
        if nid not in self.nodes:
            self.nodes[nid] = (nid, ntype, name, json.dumps(attrs, ensure_ascii=False))

    def edge(self, s, p, o, source, source_id, source_url, retrieved, evidence_type="observed", code="", confidence="", quote="", contradicted_by="", **attrs):
        assert evidence_type in EVIDENCE_TYPES and source_url, (s, p, o)
        self.edges.append([None, s, p, o, source, source_id, source_url, retrieved, evidence_type, code,
                           "" if confidence == "" else round(float(confidence), 2), quote, contradicted_by, json.dumps(attrs, ensure_ascii=False)])

    def write(self):
        part = os.path.join(SLICE, "parts")
        for i, e in enumerate(self.edges):
            e[0] = f"{self.name.upper()[:3]}{i + 1:06d}"
        write_tsv(os.path.join(part, self.name + "_nodes.tsv"), ["id", "type", "name", "attributes"], sorted(self.nodes.values()))
        write_tsv(os.path.join(part, self.name + "_edges.tsv"), EDGE_COLS, self.edges)
        from collections import Counter
        print(f"{self.name}: {len(self.nodes)} nodes {dict(Counter(n[1] for n in self.nodes.values()))} | {len(self.edges)} edges {dict(Counter(e[2] for e in self.edges))}")


OPENAI_URL = "https://api.openai.com/v1/chat/completions"
if not os.environ.get("OPENAI_API_KEY") and os.path.exists(os.path.join(ROOT, ".env")):   # .env is git-ignored
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        k, _, v = line.strip().partition("=")
        if k in ("OPENAI_API_KEY", "OPENAI_MODEL") and v:
            os.environ.setdefault(k, v.strip().strip('"').strip("'"))
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")


def openai_json(key, system, user, schema_name, schema):
    """One structured-output call to OpenAI, cached under data/slice/cache/openai/ like any other source.

    A rebuild without OPENAI_API_KEY reuses the cached answers; a call that is not cached yet needs the key.
    """
    body = {"model": OPENAI_MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_schema", "json_schema": {"name": schema_name, "strict": True, "schema": schema}}}
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", key)[:80] + "-" + hashlib.sha1((OPENAI_URL + json.dumps(body)).encode()).hexdigest()[:8]
    if not os.path.exists(os.path.join(CACHE, "openai", safe + ".json")) and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set and this call is not cached")
    res, retrieved = cached("openai", key, OPENAI_URL, data=body, headers={"Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "")},
                            min_interval=0.2, ok=lambda p: isinstance(p, dict) and p.get("choices"))
    return json.loads(res["choices"][0]["message"]["content"]), retrieved, res.get("model", OPENAI_MODEL)


def obj(**props):
    """Strict JSON schema object: every property required, nothing extra."""
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
