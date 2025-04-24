@echo off
echo 쿠팡 주문서 분석기 배포 스크립트
echo ================================

REM Git 변경사항 확인
echo.
echo 1. Git 변경사항 확인 중...
git status
echo.

REM 사용자 확인
set /p confirm=변경사항을 커밋하시겠습니까? (Y/N): 
if /i "%confirm%" neq "Y" goto end

REM 커밋 메시지 입력
set /p commit_msg=커밋 메시지를 입력하세요: 

REM 변경사항 커밋 및 푸시
echo.
echo 2. 변경사항 커밋 중...
git add .
git commit -m "%commit_msg%"
echo.

echo 3. GitHub에 푸시 중...
git push
echo.

REM 실행 파일 생성
echo 4. 실행 파일 생성 중...
pyinstaller --onefile --windowed gui_app.py
echo.

echo 5. 배포 파일 준비 중...
if not exist "dist" mkdir dist
if not exist "dist\release" mkdir dist\release

REM 현재 날짜로 폴더 생성
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set mm=%%a
    set dd=%%b
    set yy=%%c
)
set release_dir=dist\release\release_%yy%%mm%%dd%

if not exist "%release_dir%" mkdir "%release_dir%"

REM 필요한 파일 복사
copy "dist\gui_app.exe" "%release_dir%\"
copy "README.md" "%release_dir%\"

echo.
echo 배포가 완료되었습니다!
echo 배포 파일 위치: %release_dir%
echo.

:end
pause 