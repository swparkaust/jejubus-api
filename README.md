# jejubus
🚍 제주 버스 시간표 크롤러

## 설치
```
python3 -m venv myvenv
source myvenv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py updatedb --clear-history
```
