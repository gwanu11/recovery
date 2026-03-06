# Discord OAuth2 Link Bot for Render

사용자가 자신의 Discord 계정을 직접 연결하는 OAuth2 웹앱 + Discord 봇 최소 예제입니다.

## 기능
- `/login` 으로 Discord OAuth2 시작
- `/callback` 에서 authorization code 를 access token / refresh token 으로 교환
- 사용자 정보 조회 후 로컬 JSON 저장
- Discord 봇 실행
- Render Web Service 에 바로 배포 가능

## 프로젝트 구조
```text
discord_oauth_render_bot/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ bot.py
│  ├─ oauth.py
│  ├─ storage.py
│  └─ main.py
├─ templates/
│  └─ index.html
├─ data/
│  └─ users.json
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ render.yaml
└─ README.md
```

## 1) Discord Developer Portal 설정
1. Discord Developer Portal 에서 애플리케이션 생성
2. **OAuth2 > Redirects** 에 아래 URI 등록
   - 로컬: `http://localhost:10000/callback`
   - Render: `https://YOUR-SERVICE.onrender.com/callback`
3. **Bot** 탭에서 봇 생성 후 토큰 발급
4. 필요한 경우 **Privileged Gateway Intents** 활성화
5. OAuth2 scope 는 최소한 `identify` 를 사용

## 2) 환경변수
`.env.example` 를 참고해서 `.env` 파일을 만드세요.

주요 환경변수:
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_BOT_TOKEN`
- `DISCORD_REDIRECT_URI`
- `SESSION_SECRET`
- `BASE_URL`
- `BOT_GUILD_ID` (선택)

## 3) 로컬 실행
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 는 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

브라우저에서 `http://localhost:10000` 접속.

## 4) Render 배포
### 권장 방식
- **Web Service** 1개로 웹서버 + 봇 같이 실행

### 설정
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

또는 `render.yaml` 로 인프라 설정 가능.

## 5) GitHub 업로드
```bash
git init
git add .
git commit -m "Initial Discord OAuth bot"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/YOUR_REPO.git
git push -u origin main
```

## 보안 주의
- `DISCORD_CLIENT_SECRET`, `DISCORD_BOT_TOKEN` 은 절대 깃허브에 올리지 마세요.
- `.env` 는 반드시 `.gitignore` 에 포함하세요.
- 실제 운영 시 `users.json` 대신 PostgreSQL 같은 DB 사용을 권장합니다.

## 확장 아이디어
- 연동 해제 API
- refresh token 자동 갱신
- PostgreSQL 저장
- 관리자 대시보드
- 유저별 상태/메모 저장
