# 쿠팡 주문서 분석기

쿠팡 주문 데이터를 분석하여 상품별 수량을 집계하는 프로그램입니다.

## 설치 방법

1. Python 3.8 이상 설치
   - [Python 다운로드 페이지](https://www.python.org/downloads/)에서 Python 3.8 이상 버전 다운로드
   - 설치 시 "Add Python to PATH" 옵션을 반드시 체크

2. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

3. 실행 파일 생성
   ```bash
   pyinstaller --onefile --windowed gui_app.py
   ```

4. 실행
   - `dist` 폴더의 `gui_app.exe` 파일을 실행

## 사용 방법

1. 프로그램 실행
2. "엑셀 파일 선택" 버튼을 클릭하여 분석할 쿠팡 주문 엑셀 파일 선택
3. "분석하기" 버튼을 클릭하여 분석 시작
4. 분석 결과가 테이블에 표시됨
5. "엑셀 저장" 버튼을 클릭하여 결과를 엑셀 파일로 저장

## 주의사항

- Windows 10 이상 권장
- 최소 4GB RAM 필요
- 엑셀 파일은 .xlsx 형식만 지원
- 실행 파일이 있는 폴더에 쓰기 권한 필요 