# Daily News Briefing — Setup Guide (Gemini + GitHub Actions)

이 시스템은 매일 아침 커버 기업 뉴스를 **Gemini API (Google Search Grounding)** 로
수집·요약한 뒤 **Gmail SMTP**로 이메일을 보냅니다. 전체는 **GitHub Actions**가
백엔드에서 자동 실행합니다.

## 파일 구성

| 파일 | 역할 |
|------|------|
| `companies.txt` | 커버 기업 목록 (한 줄에 하나씩, `#` 줄은 무시) |
| `news_digest.py` | Gemini 검색 → 요약 → 이메일 전송 스크립트 |
| `requirements.txt` | Python 의존성 (`google-genai`) |
| `.github/workflows/daily-news.yml` | 매일 실행되는 GitHub Actions 워크플로우 |
| `.env.example` | 로컬 테스트용 환경변수 템플릿 |

## 1단계: GitHub 레포 생성

1. https://github.com/new 접속
2. 레포 이름: `news-briefing` (원하는 이름, Public)
3. **Create repository** 클릭
4. 프로젝트 폴더에서:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/news-briefing.git
git push -u origin main
```

> `.gitignore`에 `.env`가 포함되어 있어 API 키가 커밋되지 않습니다.

## 2단계: Gmail 앱 비밀번호 발급

1. https://myaccount.google.com/security 접속
2. **2단계 인증** 켜기
3. **앱 비밀번호** 검색 → 선택
4. 이름 입력 (예: `news-briefing`) → **생성**
5. 16자리 앱 비밀번호 복사 (저장)

## 3단계: Gemini API 키 발급

1. https://aistudio.google.com/apikey 접속
2. **Create API key** 클릭 → 키 복사

## 4단계: GitHub Secrets 설정

레포에서 **Settings → Secrets and variables → Actions → New repository secret**:

| 이름 | 값 |
|------|-----|
| `GEMINI_API_KEY` | Gemini API 키 (필수) |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 (필수) |
| `EMAIL_FROM` | (선택) 보내는 계정, 기본 `williamai762@gmail.com` |
| `EMAIL_TO` | (선택) 받는 계정, 기본 `williamai762@gmail.com` |
| `GEMINI_MODEL` | (선택) 기본 `gemini-2.5-flash` |

## 5단계: 테스트

레포의 **Actions** 탭에서:
1. **Daily News Briefing** 워크플로우 선택
2. **Run workflow** 클릭
3. 실행 결과 확인 후 이메일 수신 확인

## 완료!

- 스케줄: **매일 00:00 UTC = 오전 8시 (KST)** 자동 실행
- 시간 변경: `.github/workflows/daily-news.yml`의 `cron` 값을 수정
  (예: 오전 7시 KST → `15 22 * * *`, KST-9시간)
- 기업 추가/삭제: `companies.txt` 편집 후 push

## 로컬 테스트 (선택)

```bash
pip install -r requirements.txt
# .env 파일에 키 입력 후
$env:GEMINI_API_KEY="..."
$env:GMAIL_APP_PASSWORD="..."
python news_digest.py
```
