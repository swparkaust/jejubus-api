# jejubus
🚍 제주 버스 시간표 크롤러

## 설정 정보 요구사항
### 공공데이터포털 API 인증키

[공공데이터포털](https://www.data.go.kr) 가입 후 다음 서비스 신청 

* [버스노선정보조회서비스](https://www.data.go.kr/dataset/15000758/openapi.do?mypageFlag=Y)
* [버스정류소정보조회서비스](https://www.data.go.kr/dataset/15000759/openapi.do?mypageFlag=Y)

마이페이지 > OPEN API > 개발계정 상세보기 > 각 서비스별 '일반 인증키' 복사

## jejubus/settings.py 파일
```
BUS_INFO_API_KEY = '공공데이터포털에서 버스 정보조회를 위해 발급받은 인증키'
```

## 설치
```
python3 -m venv myvenv
source myvenv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py updatedb --clear-history
```
