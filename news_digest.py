import os
import sys
import time
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Missing dependency. Run: pip install -r requirements.txt")

REQUEST_TIMEOUT_SECONDS = 90

KST = timezone(timedelta(hours=9))
DEFAULT_EMAIL = "williamai762@gmail.com"
COMPANIES_FILE = "companies.txt"
MODEL = os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash"


def load_companies(path=COMPANIES_FILE):
    try:
        with open(path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    except FileNotFoundError:
        sys.exit(f"{path} not found. Create it with one company per line.")
    if not lines:
        sys.exit(f"{path} is empty. Add at least one company.")
    return lines


def search_company_news(client, company, date_str, retries=3):
    prompt = f"""당신은 금융 분석가의 뉴스 리서치 어시스턴트입니다.

오늘 날짜: {date_str}
Google 검색을 사용해 다음 기업의 가장 최신 관련 뉴스를 찾아주세요: {company}

지침:
- 최신 뉴스 우선, 중복/광고 제외, 중요 뉴스(실적, 인수합병, 규제, 기술개발 등) 우선
- 최대 3개 항목만 반환
- 각 항목은 다음 형식의 한 줄로만 출력:
  **제목** | 출처: 매체명 | 한 문장 요약
- 관련 뉴스가 없으면 정확히 "뉴스 없음"만 출력
- 위 형식 외 설명을 추가하지 마세요"""

    for attempt in range(1, retries + 1):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.2,
                ),
            )
            return resp.text.strip() if resp.text else ""
        except Exception as e:
            print(f"  [{company}] attempt {attempt} failed: {e}")
            if attempt == retries:
                return ""
            time.sleep(3)
    return ""


def build_html(results, date_str):
    rows = []
    for company, text in results:
        rows.append(f"<h4>{company}</h4>")
        if not text or text == "뉴스 없음":
            rows.append("<p>오늘 별도 뉴스 없음</p>")
        else:
            rows.append("<ul>")
            for line in text.splitlines():
                line = line.strip().lstrip("-").strip()
                if not line:
                    continue
                if "|" in line:
                    title, rest = line.split("|", 1)
                    rows.append(f"<li><b>{title.strip()}</b> - {rest.strip()}</li>")
                else:
                    rows.append(f"<li>{line}</li>")
            rows.append("</ul>")

    sections = "\n".join(rows)
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
      <h2>📅 일일 기업 뉴스 브리핑 - {date_str}</h2>
      <p>아래는 Gemini(Google Search)로 수집한 커버 기업 뉴스 요약입니다.</p>
      <hr>
      <h3>📊 기업별 뉴스</h3>
      {sections}
      <hr>
      <p><i>이 뉴스는 자동으로 수집 및 정리되었습니다.</i></p>
    </body>
    </html>
    """


def send_email(html_content, date_str, from_addr, to_addr, app_password):
    subject = f"[일일 뉴스 브리핑] 커버 기업 뉴스 정리 - {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_addr, app_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
    print(f"Email sent to {to_addr}")


def main():
    from_addr = os.environ.get("EMAIL_FROM", DEFAULT_EMAIL)
    to_addr = os.environ.get("EMAIL_TO", DEFAULT_EMAIL)
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        sys.exit("GEMINI_API_KEY environment variable is required.")
    if not app_password:
        sys.exit("GMAIL_APP_PASSWORD environment variable is required.")

    date_str = datetime.now(KST).strftime("%Y년 %m월 %d일")
    companies = load_companies()
    print(f"Found {len(companies)} companies. Model: {MODEL}")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_SECONDS * 1000),
    )

    results = []
    for i, company in enumerate(companies):
        print(f"[{i + 1}/{len(companies)}] Searching news for {company}...", flush=True)
        text = search_company_news(client, company, date_str)
        results.append((company, text))

    html = build_html(results, date_str)
    send_email(html, date_str, from_addr, to_addr, app_password)


if __name__ == "__main__":
    main()
