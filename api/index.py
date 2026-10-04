"""Vercel entry point: the same request handler as `python -m atlas.server`, one Application per instance.

vercel.json rewrites /api/<path> to /api/index?__path=<path>; the original path is restored before routing,
so routing, validation and security headers are identical to the local server.
"""
import os
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('ATLAS_SERVERLESS', '1')   # before importing atlas: writable paths move to /tmp

from atlas.server import Application, make_handler  # noqa: E402

APP = Application()
_Handler = make_handler(APP)


def original_path(path):
    parts = urlsplit(path)
    query = parse_qsl(parts.query, keep_blank_values=True)
    target = next((value for key, value in query if key == '__path'), None)
    if target is None:   # already the original path; drop any scheme/host the runtime may include
        return parts.path + ('?' + parts.query if parts.query else '')
    rest = [(key, value) for key, value in query if key != '__path']
    return '/api/' + target.lstrip('/') + ('?' + urlencode(rest) if rest else '')


class handler(_Handler):
    def do_GET(self):
        self.path = original_path(self.path)
        super().do_GET()

    def do_POST(self):
        self.path = original_path(self.path)
        super().do_POST()
