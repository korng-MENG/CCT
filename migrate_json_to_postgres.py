import argparse, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).with_name('.env'))
from cct_storage import init_db, read_state, write_state

parser = argparse.ArgumentParser(description='Import the CCT Express JSON database into PostgreSQL JSONB.')
parser.add_argument('--file', default='database/source/cct_database(3).json')
parser.add_argument('--force', action='store_true', help='Replace the current PostgreSQL state (use only after a backup).')
args = parser.parse_args()
source = Path(args.file)
if not source.is_file():
    raise SystemExit(f'Source JSON not found: {source}')
data = json.loads(source.read_text(encoding='utf-8'))
if not isinstance(data, dict):
    raise SystemExit('Invalid database: expected a JSON object.')
init_db()
current = read_state()
if current is not None and not args.force:
    raise SystemExit('PostgreSQL already contains CCT data. Stop: use --force only if you intend to replace it.')
write_state(data)
print('Import successful.')
for key, value in data.items():
    if isinstance(value, (list, dict)):
        print(f'{key}: {len(value)}')
