import importlib.util
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_FILE = os.path.join(BASE_DIR, "cct_telegram_bot-v2.py")

spec = importlib.util.spec_from_file_location("cct_backend", BACKEND_FILE)
backend = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backend
spec.loader.exec_module(backend)

backend.init_db()
app = backend.app
