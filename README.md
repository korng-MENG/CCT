# CCT EXPRESS — Vue 3 + Flask + Telegram + PostgreSQL

## ស្ថានភាពកំណែនេះ
នេះជាកំណែ Phase 1 សម្រាប់បន្តពី Vue 3 project ដែលបានបង្កើតរួច។ Vue 3/Vite/Pinia ជា Frontend shell; legacy workflows ត្រូវបានរក្សាទុកជាបណ្ណាល័យ JavaScript compatibility ដើម្បីកុំឱ្យបាត់ Invoice, Barcode/QR, POS-80, Excel, Reports និង Driver Scan។ Backend នៅជា Python Flask + Telegram Bot។

PostgreSQL ក្នុង Phase 1 រក្សាទម្រង់ទិន្នន័យ JSON ដើមក្នុងជួរឈរ JSONB តែមួយ ដើម្បីឱ្យ API និង Bot logic ចាស់អាចប្រើបានដោយមិនបម្លែង field names ឬបាត់ទិន្នន័យ។ វាជាជំហាន compatibility; ការបំបែកជា relational tables នឹងធ្វើនៅ Phase បន្ទាប់ក្រោយសាកល្បង workflow ទាំងអស់។

## 1) Ubuntu Server VM
សម្រាប់ឱ្យ LAN និង Internet អាចចូលបាន សូមកំណត់ Network Adapter របស់ VM ជា **Bridged Adapter** (ឬ NAT + Port Forwarding) ហើយកំណត់ DHCP Reservation/static IP នៅ Router។ មុនបើកពី Internet ត្រូវមាន Domain និង HTTPS។ Camera scan នៅលើ browser ត្រូវការប្រើ HTTPS (លើកលែង localhost)។

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib nginx git curl
```

Install Node.js 22 LTS (build frontend):
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node -v && npm -v
```

## 2) PostgreSQL
```bash
sudo -u postgres psql
```
Inside `psql` (replace the password with a strong unique password):
```sql
CREATE USER cct_app WITH PASSWORD 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';
CREATE DATABASE cct_express OWNER cct_app;
\q
```

## 3) Configure and import existing data
From the project root:
```bash
cp .env.example .env
nano .env
```
Set `DATABASE_URL` to the password you created. Leave `CCT_BOT_TOKEN` blank until you create a **new token** with @BotFather. A real token was exposed in the original uploaded Python file; revoke it and do not reuse it.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python migrate_json_to_postgres.py
```
The importer stops if PostgreSQL already has data. Only use `--force` when you deliberately want to replace the current state after backing it up.

## 4) Build Vue 3 frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

## 5) Start for local/LAN testing
```bash
source .venv/bin/activate
python cct_telegram_bot-v2.py
```
Open `http://VM_IP/` after configuring Nginx, or temporarily `http://VM_IP:5000/` for direct Flask testing. The app's route aliases `/`, `/vip/cct8899`, and `/driver` are retained.

## 6) Nginx + HTTPS
Copy `deploy/nginx-cct-express.conf` to `/etc/nginx/sites-available/cct-express`, replace `YOUR_DOMAIN_OR_SERVER_IP`, enable it, then test:
```bash
sudo ln -s /etc/nginx/sites-available/cct-express /etc/nginx/sites-enabled/cct-express
sudo nginx -t && sudo systemctl reload nginx
```
When your domain DNS points to the public IP and router forwards TCP 80/443 to the VM:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.example
```

## 7) Run as a service
Create a dedicated Linux user and copy the project to `/opt/cct-express-vue3`, set ownership and permissions, then install the unit:
```bash
sudo useradd --system --home /opt/cct-express-vue3 --shell /usr/sbin/nologin cctexpress
sudo chown -R cctexpress:cctexpress /opt/cct-express-vue3
sudo cp deploy/cct-express.service /etc/systemd/system/cct-express.service
sudo systemctl daemon-reload
sudo systemctl enable --now cct-express
sudo systemctl status cct-express
```

## Notes / safety before Internet exposure
- The current legacy API has login and role checks mainly in the frontend; `/api/state` and `/api/users` are not yet protected by server-side sessions/authorization. Do **not** expose this build publicly until Phase 2 adds server-side authentication, per-role API authorization, rate limits, secure cookies/CSRF protections, and audit logging.
- Change all default/weak user passwords before deployment. The imported database contains user records and delivery/customer data; protect `.env`, PostgreSQL, backups and uploaded proof photos.
- Keep `CCT_BOT_TOKEN` only in `.env` on the server. Never paste it into the browser or commit `.env` to Git.
- If barcode image decoding is needed on Ubuntu, install `sudo apt install -y libzbar0 tesseract-ocr`; OCR/barcode Python packages are listed in requirements.
- Keep exactly one application process while using the compatibility JSONB state store, so concurrent whole-state writes do not overwrite each other.

## Existing functions carried forward
Invoice auto numbering, barcode/QR preview, POS-80 printing, Excel import/export, reports, shops/users, login view, driver camera scan/photo proof, Telegram bot and group notifications are preserved in the compatibility layer. Validate each workflow against the live system before switching all staff to this version.
