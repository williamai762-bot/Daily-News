# 뉴스 브리핑 자동 실행 스크립트
# Windows 작업 스케줄러에서 매일 오전 8시에 실행되도록 설정

$projectPath = "C:\Users\seoks\OneDrive - The University of Hong Kong\문서\Default Project"
$logFile = "$projectPath\news-daily.log"

# 로그 함수
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append -Encoding utf8
}

try {
    Write-Log "뉴스 브리핑 시작"
    
    # opencode 실행 (非 interactive 모드로/news-daily 커맨드 실행)
    Set-Location -LiteralPath $projectPath
    
    # 환경변수에서 Gmail App Password 확인
    if (-not $env:GMAIL_APP_PASSWORD) {
        Write-Log "오류: GMAIL_APP_PASSWORD 환경변수가 설정되지 않았습니다."
        exit 1
    }
    
    # opencode 실행 - news-daily 커맨드 호출
    # $env:GMAIL_APP_PASSWORD는 에이전트가 PowerShell에서 사용할 수 있어야 함
    & opencode --command "news-daily" 2>&1 | Out-File -FilePath $logFile -Append -Encoding utf8
    
    Write-Log "뉴스 브리핑 완료"
}
catch {
    Write-Log "오류 발생: $_"
    exit 1
}
