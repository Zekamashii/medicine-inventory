# 医薬品在庫管理システム

## 📓Description

A medicine inventory management system. The [MS852](https://www.ute.com/jp/products/detail/MS852) scanner is recommended.

## 🕹Built with

- [Python 3.12](https://www.python.org/doc/)
- [Django 5](https://docs.djangoproject.com/en/5.0/)
- jQuery - Ajax
- SQLite
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/), Theme: [Flatly](https://bootswatch.com/flatly/)
- [Docker](https://docs.docker.com/)
- [Nginx](https://www.nginx.com/)
- [Gunicorn](https://gunicorn.org/)
- [Certbot](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

## 📁File Structure
<details>
<summary>File tree</summary>

```bash
.
├── Dockerfile
├── README.md
├── ckstock
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                      # Adjust Django settings here
│   ├── urls.py
│   └── wsgi.py
├── database                             # Database folder
│   └── db.sqlite3
├── docker-compose-initiate.yaml         # For first run only
├── docker-compose.yml
├── inventory
│   ├── CsrfLoggingMiddleware.py
│   ├── SetDefaultSiteCookieMiddleware.py # A middleware to set user default site after logging in
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── csv_download.py                 # A function to generate CSV files from the transaction history
│   ├── databar_analyzer.py             # A function to analyze GS1 databar and return drug information
│   ├── forms.py
│   ├── input_normalizer.py             # Pythonで文字列をUnicode正規化 (https://note.nkmk.me/python-unicodedata-normalize/)
│   ├── models.py
│   ├── resources.py                    # For Drug Master import/export
│   ├── signals.py
│   ├── static                          # Static files
│   ├── templates
│   │   └── inventory
│   │       ├── adjust_form.html        # 在庫調整
│   │       ├── base.html
│   │       ├── bottom.html             # Text at the bottom of the sidebar
│   │       ├── calendar.html           # 在庫予測
│   │       ├── cancel_form.html        # 入出庫を取り消し
│   │       ├── category.html           # 医薬品種類
│   │       ├── category_form.html      # 医薬品種類を追加編集するフォーム
│   │       ├── confirm_transfer.html   # 拠点間移動を確認
│   │       ├── dashboard.html          # 在庫一覧
│   │       ├── drug_master.html        # 医薬品マスター
│   │       ├── drug_master_form.html   # 医薬品マスターを追加編集するフォーム
│   │       ├── errors                  # Customized error pages
│   │       │   ├── 400.html
│   │       │   ├── 403.html
│   │       │   ├── 404.html
│   │       │   ├── 500.html
│   │       │   └── csrf_failure.html
│   │       ├── import_drug_master.html # 医薬品マスターをインポート
│   │       ├── index.html              # 挨拶ページ
│   │       ├── login.html              # ログイン
│   │       ├── logout.html             # ログアウト
│   │       ├── navigation.html         # Navigation bar on the top
│   │       ├── pagination.html         # 複数ページに表示
│   │       ├── pending_confirmations.html # 拠点間移動：受領確認待ちリスト
│   │       ├── populate_kana.html      # 開発者機能：すべての医薬品の仮名を設定する
│   │       ├── populate_safety_stock.html # 開発者機能：すべての医薬品および拠点の安全在庫を設定する
│   │       ├── safety_stock_matrix.html # 定数を設定
│   │       ├── sidebar.html            # Sidebar on the left
│   │       ├── signup.html             # 会員登録
│   │       ├── site.html               # 拠点管理
│   │       ├── site_form.html          # 拠点を追加編集するフォーム
│   │       ├── transaction.html        # 入出庫履歴照会
│   │       ├── transaction_form.html   # 入出庫を追加するフォーム
│   │       ├── user.html               # ユーザー一覧
│   │       ├── user_form.html          # ユーザー設定を編集
│   │       └── validate_inventory.html # 不一致レポート
│   ├── tests.py
│   ├── urls.py                         # Router settings
│   └── views.py
├── manage.py
├── proxy                               # Nginx config files
│   ├── Dockerfile
│   ├── default.conf.tpl
│   ├── initiate                        # For first run only
│   │   ├── Dockerfile
│   │   ├── default.conf.tpl
│   │   └── start.sh
│   ├── proxy_params
│   └── start.sh
├── requirements.txt
└── scripts
    └── start.sh                      # Django & Gunicorn scripts

```
</details>

## 👩‍💻Development Environment Setup

Clone the repo.

Create a .env file.

It is something like this:

```python
ALLOWED_DOMAINS = ['xxx.com']
DEBUG = True
SECRET_KEY = ""
EMAIL = "xxx@xxx.com"
DOMAIN = "xxx.com"
```

Set `DEBUG = True`.
```bash
pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver 127.0.0.1:8000
```

## 🚢AWS/Docker Environment Setup & Operation
### References

[1] [Serving static and media files using Nginx in Django](https://medium.com/django-unleashed/serving-static-and-media-files-using-nginx-in-django-a4a125af95d)

[2] [An Elegant way to use docker-compose to obtain and renew a Let’s Encrypt SSL certificate with Certbot and configure the NGINX service to use it](https://blog.jarrousse.org/2022/04/09/an-elegant-way-to-use-docker-compose-to-obtain-and-renew-a-lets-encrypt-ssl-certificate-with-certbot-and-configure-the-nginx-service-to-use-it/)

### Architecture
<img src="https://raw.githubusercontent.com/Aikoyori/ProgrammingVTuberLogos/main/Docker/DockerLogo.png" height="250" align="center"/>

Three containers will be created:
```sh
CONTAINER ID   IMAGE                    COMMAND                  CREATED      STATUS                   PORTS                                                                      NAMES
xxxxxxxxxxxx   certbot/certbot:latest   "certbot certonly --…"   2 days ago   Exited (0) 2 hours ago                                                                              certbot-container
xxxxxxxxxxxx   ck-stock-proxy           "sh -c /start.sh"        2 days ago   Up 2 days                0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp   nginx-container
xxxxxxxxxxxx   ck-stock-app             "sh -c ./scripts/sta…"   2 days ago   Up 2 days                                                                                           django-container
```

```bash
  +------------------------------------------------+
  | Proxy Service (nginx-container)                |
  | Ports: 80:80, 443:443                          |
  | Volumes: static-data, database, certbot config |
  +------------------------------------------------+
         | depends on
         v
  +-------------------------------+
  | App Service (django-container)|
  | Volumes: static-data, database|
  +-------------------------------+

Proxy and App share volumes: static-data, database

  +------------------------------------------------+
  | Certbot Service (certbot-container)            |
  +------------------------------------------------+
         | depends on
         v
  | External Ports                                 |
  | 80 -> Proxy, 443 -> Proxy                      |
  +------------------------------------------------+
```

### Instructions

Clone the repo in the AWS instance.

Create a .env file or download the file from Bitwarden.

Set `DEBUG = False`.
```bash
# FIRST RUN ONLY 
# The only difference is that the Nginx conf is adjusted for Certbot to create a new certificate
git clone git@github.com:xxx/ck-stock.git
sudo docker compose -f ./docker-compose-initiate.yaml up --build --remove-orphans --force-recreate -d

# For future updates
git pull
sudo docker compose up --build --remove-orphans -d

# See logs
docker compose logs

# For manual certificate renewal
docker compose start certbot

# List all containers
docker ps -a
# Check logs for a specific container
docker logs -f [Container ID]

# Run commands inside containers
docker exec -it [Container ID] sh
python manage.py createsuperuser # Save the username and the password to Bitwarden

### Copy DB file from the container to the EC2 local directory
docker cp [Container ID]:/app/database/db.sqlite3 backup
# Download the file using Cyberduck

### Copy local DB file into Docker container
### Extremely useful when `makemigrations` fails to work
docker cp [filename] [Container ID]:/app/database/

# Clean Docker cache and free up disk space
# Use docker system prune WILL DELETE certbot container
docker buildx prune --all

# To list file sizes
ncdu

# To monitor resource usage inside the EC2 instance
htop
```

Log in into `/admin` page as the superuser and create a unit named 'EA'.
### Automatic Certificate Renewal
Install [`Crontab`](https://crontab.guru/) for an automatic task scheduling.
```sh
sudo apt-get install cron

# Edit crontab
crontab -e

# Add this line to run the task monthly
0 0 1 * * cd /home/ubuntu/ck-stock && docker compose start certbot

# View the content of crontab
crontab -l
```

## 📝User Documentation
[CK-Stock マニュアル](https://tbc-4.gitbook.io/ck-stock-knowledge-base/ck-stock-manyuaru)
