"""Where the app may write, and whether it runs as serverless functions (Vercel).

Locally everything lives under data/. On Vercel only /tmp is writable, it is per instance and
temporary, and background threads stop when a response is sent.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVERLESS = bool(os.environ.get('ATLAS_SERVERLESS') or os.environ.get('VERCEL'))
DATA_DIR = Path(os.environ.get('ATLAS_DATA_DIR') or ('/tmp/asterisk' if SERVERLESS else ROOT / 'data'))
