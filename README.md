# Discord OAuth2 Recovery Bot for Render

사용자가 자신의 Discord 계정을 직접 연결하고, 나중에 특정 관리자만 `/복구` 명령어로 **그 명령어를 실행한 서버**에 다시 추가를 시도하는 예제입니다.

## 포함 기능
- `/login` 으로 Discord OAuth2 시작
- OAuth2 scope: `identify guilds.join`
- `/callback` 에서 authorization code 를 access token / refresh token 으로 교환
- 사용자 정보와 토큰을 SQLite 데이터베이스에 저장
- `/복구` 명령어 실행 시 현재 서버(`interaction.guild_id`)를 대상으로 복구 시도
- `/복구`, `/연동수`, `/핑` 슬래시 명령어 제공
- 특정 Discord 사용자 ID만 `/복구` 실행 가능
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
│  └─ app.db
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ render.yaml
└─ README.md
```

## 필수 Discord 설정
1. Discord Developer Portal 에서 애플리케이션 생성
2. **OAuth2 > Redirects** 에 아래 URI 등록
   - 로컬: `http://localhost:10000/callback`
   - Render: `https://YOUR-SERVICE.onrender.com/callback`
3. **Bot** 탭에서 봇 생성 후 토큰 발급
4. 봇을 사용할 서버에 초대
5. OAuth2 동의 범위는 코드에서 `identify guilds.join` 으로 처리됨

## 환경변수
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_BOT_TOKEN`
- `DISCORD_REDIRECT_URI`
- `SESSION_SECRET`
- `BASE_URL`
- `ALLOWED_ADMIN_USER_ID`
- `DATABASE_PATH`

## 로컬 실행
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 는 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

## Render 설정
- Root Directory: 비움
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Render 환경변수 예시
```text
DISCORD_CLIENT_ID=...
DISCORD_CLIENT_SECRET=...
DISCORD_BOT_TOKEN=...
DISCORD_REDIRECT_URI=https://YOUR-SERVICE.onrender.com/callback
BASE_URL=https://YOUR-SERVICE.onrender.com
SESSION_SECRET=long_random_string
ALLOWED_ADMIN_USER_ID=123456789012345678
DATABASE_PATH=data/app.db
```

## 명령어 설명
- `/핑`: 봇 상태 확인
- `/연동수`: 현재 연동된 사용자 수 표시
- `/복구`: **오직 `ALLOWED_ADMIN_USER_ID` 에 지정한 유저만** 실행 가능
  - 실행된 서버를 대상으로 함
  - DB 에 저장된 동의 사용자들을 순회
  - 먼저 저장된 access token 으로 추가 시도
  - 401 이면 refresh token 으로 갱신 후 재시도

## 주의
- `.env` 는 깃허브에 올리지 마세요.
- SQLite 파일은 테스트/소규모 운영용입니다.
- Discord 쪽 권한, 멤버십 스크리닝, 토큰 만료 상태에 따라 일부 사용자는 복구 실패할 수 있습니다.
- Render 무료 플랜 슬립 회피용 자기 핑 코드는 넣지 않았습니다.

## GitHub 업로드
```bash
git init
git add .
git commit -m "Initial Discord OAuth recovery bot"
git branch -M main
git remote add origin https://github.com/YOUR_NAME/YOUR_REPO.git
git push -u origin main
```
