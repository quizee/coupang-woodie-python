import re
from collections import defaultdict
import pandas as pd
import os
import sys
from datetime import datetime

def normalize_product_name(name):
    """
    상품명을 표준화합니다.
    - 띄어쓰기 제거
    - 할리피뇨 -> 할라피뇨 통일
    - 비건 올리브 치아바타 -> 올리브치아바타 통일
    - 우디베이크샵 매콤 할라피뇨 치아바타 -> 할라피뇨치아바타 통일
    - 5가지맛 셋트 -> 5가지맛셋트 통일
    """
    if not isinstance(name, str):
        return name

    # 비건 올리브 치아바타 -> 올리브치아바타 통일
    if re.search(r'비건\s+올리브(\s+치아바타)?\s+\d+개입.*', name, re.IGNORECASE):
        return "올리브치아바타"

    # 우디베이크샵 매콤 할라피뇨 치아바타 -> 할라피뇨치아바타 통일
    if re.search(r'우디베이크샵.*할라피뇨.*치아바타', name, re.IGNORECASE):
        return "할라피뇨치아바타"

    # 5가지맛 셋트 -> 5가지맛셋트 통일
    if any(set_name in name for set_name in ["5가지맛 셋트", "5가지맛 세트", "5가지 맛 셋트", "5가지 맛 세트"]):
        return "5가지맛셋트"

    # 띄어쓰기 제거
    for category in ["올리브", "치즈", "할라피뇨", "할리피뇨", "나폴리", "플레인"]:
        # "올리브 치아바타" -> "올리브치아바타"로 변환
        pattern = f"{category}\\s+치아바타"
        if re.search(pattern, name):
            name = re.sub(pattern, f"{category}치아바타", name)

    # 할리피뇨 -> 할라피뇨 통일
    if "할리피뇨" in name:
        name = name.replace("할리피뇨", "할라피뇨")

    return name

def process_original_format(text, product_counts):
    """
    처음 제시된 양식(이름으로 시작하는 줄 + 상품 줄)을 처리합니다.
    """
    # 각 줄 처리
    lines = text.strip().split('\n')
    current_person = None

    # 정의된 카테고리 목록 - 정확히 이 목록에 없는 상품은 모두 "그 외 상품"으로 분류
    categories = ["플레인", "올리브", "치즈", "할라피뇨", "할리피뇨", "나폴리", "올식", "연유",
                 "먹식", "시식", "시브", "넛츠", "깜", "단호박", "밤", "팥", "통밀단팥",
                 "통밀", "잡곡", "호밀", "소금", "먹소금"]

    for line in lines:
        # 숫자로 시작하는 줄은 새로운 사람 정보로 간주
        if re.match(r'^\d+\s+\S+', line):
            # 사람 이름은 무시하고 넘어감
            continue

        # 상품 정보가 있는 줄 처리
        elif line.strip():
            # 인식된 카테고리 여부 확인용
            found_category = False

            # 카테고리별 처리
            for category in categories:
                # 카테고리 이름과 숫자 찾기
                pattern = f'{category}(\\d+)'
                matches = re.finditer(pattern, line)

                for match in matches:
                    found_category = True
                    count = int(match.group(1))
                    normalized_category = category

                    # 할리피뇨를 할라피뇨로 통일
                    if category == "할리피뇨":
                        normalized_category = "할라피뇨"

                    # "치아바타" 접미사 추가 (필요한 카테고리에만)
                    if category in ["플레인", "올리브", "치즈", "할라피뇨", "할리피뇨", "나폴리"]:
                        product_counts[f"{normalized_category}치아바타"] += count
                    else:
                        product_counts[normalized_category] += count

            # 어떤 카테고리에도 매칭되지 않는 상품은 그외 상품으로 분류
            if not found_category:
                # 다른 패턴 확인 (예: "오징1", "애플1" 등)
                other_pattern = r'[가-힣]+(\\d+)'
                other_matches = re.findall(other_pattern, line)

                if other_matches:
                    for match in other_matches:
                        try:
                            quantity = int(match)
                            product_counts["그 외 상품"] += quantity
                        except ValueError:
                            # 숫자 변환 실패시 기본값 1
                            product_counts["그 외 상품"] += 1
                else:
                    # 패턴을 찾을 수 없는 경우 기본값 1로 처리
                    # (라인에 상품 정보가 있다면)
                    if re.search(r'[가-힣]+', line):
                        product_counts["그 외 상품"] += 1

def process_option(option, product_counts, quantity_multiplier=1):
    """
    개별 옵션 정보를 처리하여 상품명과 수량을 추출합니다.
    """
    if not isinstance(option, str):
        return

    print("\n처리중인 옵션:", option)
    
    # 쉼표로 분리 (먼저 분리하고 나서 정규화)
    parts = option.split(',', 1)
    product_name = parts[0].strip()
    quantity_info = parts[1].strip() if len(parts) > 1 else ""
    
    print(f"상품명: {product_name}")
    print(f"수량 정보: {quantity_info}")
    print(f"구매 수량 배수: {quantity_multiplier}")

    # 5가지맛셋트 처리
    if "5가지맛셋트" in product_name:
        print("5가지맛셋트 처리:")
        # 수량 정보에서 개수 추출
        quantity = 1
        quantity_match = re.search(r'(\d+)개(?!\s*입)', quantity_info)
        if quantity_match:
            quantity = int(quantity_match.group(1))
        # 5가지 맛 각각 추가
        for flavor in ["플레인치아바타", "올리브치아바타", "치즈치아바타", "할라피뇨치아바타", "나폴리치아바타"]:
            product_counts[flavor] += quantity * quantity_multiplier
            print(f"  - {flavor} +{quantity * quantity_multiplier}개 추가")
        return

    # 일반 케이스: 쉼표 뒷부분에서 수량 추출
    if not quantity_info:
        print("수량 정보 없음, 기본값 1개 처리")
        product_counts[product_name] += quantity_multiplier
        print(f"  - {product_name} +{quantity_multiplier}개 추가")
        return

    # 케이스 1: "상품명,10개 올리브치아바타 10개입" -> 치아바타 종류별 처리
    chiabatta_pattern = r'(\d+)개\s+([가-힣]+)(?:\s*치아바타)'
    chiabatta_matches = re.findall(chiabatta_pattern, quantity_info)
    if chiabatta_matches:
        print("치아바타 종류별 처리:")
        for quantity, chiabatta_type in chiabatta_matches:
            normalized_name = f"{normalize_product_name(chiabatta_type)}치아바타"
            product_counts[normalized_name] += int(quantity) * quantity_multiplier
            print(f"  - {normalized_name} +{int(quantity) * quantity_multiplier}개 추가")
        return

    # 케이스 2 & 3: "상품명,1개" 또는 "상품명,100g 3개" -> 수량 추출
    quantity_match = re.search(r'(\d+)개(?!\s*입)', quantity_info)
    if quantity_match:
        print("일반 수량 패턴 처리:")
        quantity = int(quantity_match.group(1))
        
        # 케이스 5: "상품명,100g 1개 옵션명" -> 옵션명 추출
        option_name_match = re.search(r'\d+개\s+([가-힣]+(?:\s*치아바타)?(?:\s*쿠키)?)', quantity_info)
        if option_name_match:
            option_name = normalize_product_name(option_name_match.group(1))
            product_counts[option_name] += quantity * quantity_multiplier
            print(f"  - {option_name} +{quantity * quantity_multiplier}개 추가")
        else:
            product_counts[product_name] += quantity * quantity_multiplier
            print(f"  - {product_name} +{quantity * quantity_multiplier}개 추가")
        return

    # 케이스 4: "상품명,올리브치아바타 5개 + 치즈치아바타 5개" -> 치아바타 종류별 처리
    if '+' in quantity_info:
        print("치아바타 조합 패턴 처리:")
        chiabatta_pattern = r'([가-힣]+)(?:\s*치아바타)\s*(\d+)개'
        chiabatta_matches = re.findall(chiabatta_pattern, quantity_info)
        if chiabatta_matches:
            for chiabatta_type, quantity in chiabatta_matches:
                normalized_name = f"{normalize_product_name(chiabatta_type)}치아바타"
                product_counts[normalized_name] += int(quantity) * quantity_multiplier
                print(f"  - {normalized_name} +{int(quantity) * quantity_multiplier}개 추가")
            return

    # 기본 처리
    print("수량 패턴 없음, 기본값 1개 처리:")
    product_counts[product_name] += quantity_multiplier
    print(f"  - {product_name} +{quantity_multiplier}개 추가")

def analyze_text_data(text):
    """
    텍스트 형식의 주문 데이터를 분석합니다.
    """
    # 상품별 수량을 저장할 딕셔너리
    product_counts = defaultdict(int)

    # 텍스트 형식 판단
    # 쉼표(,)가 많이 포함되어 있으면 쿠팡 엑셀 내보내기 형식, 아니면 원래 형식으로 간주
    comma_count = text.count(',')
    line_count = text.count('\n') + 1

    if comma_count > line_count * 0.3:  # 30% 이상의 줄에 쉼표가 있으면 쿠팡 형식으로 간주
        # 쿠팡 엑셀 내보내기 형식 처리
        # 각 줄 처리
        lines = text.strip().split('\n')

        # 옵션명이 포함된 필드 찾기
        for line in lines:
            # 쉼표가 포함된 필드 찾기
            fields = line.split()
            for field in fields:
                if ',' in field:
                    # 올바른 형식인지 확인 (상품명,수량)
                    if re.search(r'.+,.+', field):
                        process_option(field, product_counts)
    else:
        # 원래 형식 처리 (이름 + 상품줄)
        process_original_format(text, product_counts)

    return product_counts

def analyze_excel_data(file_path):
    """
    엑셀 파일 형식의 주문 데이터를 분석합니다.
    """
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)

        # P열(최초등록등록상품명/옵션명) 찾기
        option_column_name = None
        quantity_column_name = None

        for col in df.columns:
            if "최초등록등록상품명/옵션명" in col:
                option_column_name = col
            if "구매수(수량)" in col:
                quantity_column_name = col

        if not option_column_name:
            # 열 이름으로 찾지 못한 경우 15번째 열 사용 (0-based 인덱스, P열)
            if len(df.columns) > 15:
                option_column_name = df.columns[15]

        if not quantity_column_name:
            # 구매수(수량) 열을 찾지 못한 경우 22번째 열 사용 (0-based 인덱스, 22열)
            if len(df.columns) > 22:
                quantity_column_name = df.columns[22]

        # 상품별 수량을 저장할 딕셔너리
        product_counts = defaultdict(int)

        if option_column_name:
            # 각 행을 처리
            for i, row in df.iterrows():
                option = row[option_column_name] if not pd.isna(row[option_column_name]) else ""

                # 구매수(수량) 가져오기
                quantity_multiplier = 1
                if quantity_column_name and not pd.isna(row[quantity_column_name]):
                    try:
                        quantity_multiplier = int(row[quantity_column_name])
                    except (ValueError, TypeError):
                        quantity_multiplier = 1

                if isinstance(option, str) and option:
                    process_option(option, product_counts, quantity_multiplier)
        else:
            # 열을 찾지 못한 경우, 모든 열에서 쉼표가 포함된 필드 검색
            for _, row in df.iterrows():
                for value in row:
                    if isinstance(value, str) and ',' in value:
                        # 올바른 형식인지 확인
                        if re.search(r'.+,.+', value):
                            process_option(value, product_counts)

        return product_counts

    except Exception as e:
        print(f"엑셀 파일 분석 중 오류 발생: {str(e)}")
        return None

def analyze_excel_data_by_buyer(file_path):
    """
    엑셀 파일에서 수취인별로 주문 데이터를 분석합니다.
    """
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        
        # 필요한 열 찾기
        buyer_name_column = None
        buyer_phone_column = None
        option_column_name = None
        quantity_column_name = None

        for col in df.columns:
            if "수취인이름" in col:  # '구매자' -> '수취인이름'으로 변경
                buyer_name_column = col
            if "수취인전화번호" in col:  # '구매자전화번호' -> '수취인전화번호'로 변경
                buyer_phone_column = col
            if "최초등록등록상품명/옵션명" in col:
                option_column_name = col
            if "구매수(수량)" in col:
                quantity_column_name = col

        if not buyer_phone_column:
            print("수취인 전화번호 열을 찾을 수 없습니다.")
            return None

        if not option_column_name:
            # 열 이름으로 찾지 못한 경우 15번째 열 사용 (0-based 인덱스, P열)
            if len(df.columns) > 15:
                option_column_name = df.columns[15]

        if not quantity_column_name:
            # 구매수(수량) 열을 찾지 못한 경우 22번째 열 사용 (0-based 인덱스, 22열)
            if len(df.columns) > 22:
                quantity_column_name = df.columns[22]

        # 수취인별 상품 수량을 저장할 딕셔너리
        buyer_product_counts = {}
        
        # 수취인별로 그룹화하여 처리
        for _, row in df.iterrows():
            # 전화번호는 필수
            phone = row[buyer_phone_column]
            if pd.isna(phone):
                continue
            
            # 수취인명이 있으면 사용, 없으면 '고객'으로 표시
            buyer = row[buyer_name_column] if buyer_name_column and not pd.isna(row[buyer_name_column]) else '고객'
            
            # 수취인 키 생성 (수취인명(전화번호) 형식)
            buyer_key = f"{buyer}({phone})"
            
            if buyer_key not in buyer_product_counts:
                buyer_product_counts[buyer_key] = defaultdict(int)
            
            # 상품 옵션 정보 처리
            option = row[option_column_name] if not pd.isna(row[option_column_name]) else ""
            
            # 구매수(수량) 가져오기
            quantity_multiplier = 1
            if quantity_column_name and not pd.isna(row[quantity_column_name]):
                try:
                    quantity_multiplier = int(row[quantity_column_name])
                except (ValueError, TypeError):
                    quantity_multiplier = 1

            # 상품 정보 처리
            if isinstance(option, str) and option:
                process_option(option, buyer_product_counts[buyer_key], quantity_multiplier)
        
        return buyer_product_counts
        
    except Exception as e:
        print(f"엑셀 파일 분석 중 오류 발생: {str(e)}")
        return None

def process_and_display_results(product_counts, title="쿠팡 주문 분석 결과"):
    """
    분석 결과를 처리하고 화면에 표시합니다.
    """
    if not product_counts:
        return None

    # 결과를 데이터프레임으로 변환
    df = pd.DataFrame(list(product_counts.items()), columns=['상품명', '수량'])
    df = df.sort_values('상품명')  # 상품명으로 정렬
    df['수량'] = df['수량'].astype(str) + '개'

    # 결과 출력
    print(f"\n{title}")
    print("=" * 50)
    print(df.to_string(index=False))
    print("=" * 50)

    # CSV 파일로 저장
    output_filename = "쿠팡주문분석결과.csv"
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n분석 결과가 {output_filename} 파일로 저장되었습니다.")

    return df

def process_and_display_buyer_results(buyer_product_counts, title="구매자별 주문 분석 결과"):
    """
    구매자별 분석 결과를 처리하고 화면에 표시합니다.
    """
    if not buyer_product_counts:
        return None

    print(f"\n{title}")
    print("=" * 50)
    
    # 전체 합계를 계산할 딕셔너리
    total_counts = defaultdict(int)
    
    # 각 구매자별로 결과 출력
    for buyer, product_counts in buyer_product_counts.items():
        print(f"\n[구매자: {buyer}]")
        # 구매자별 데이터프레임 생성 및 출력
        df = pd.DataFrame(list(product_counts.items()), columns=['상품명', '수량'])
        df = df.sort_values('상품명')
        df['수량'] = df['수량'].astype(str) + '개'
        print(df.to_string(index=False))
        
        # 전체 합계에 더하기
        for product, count in product_counts.items():
            total_counts[product] += count
    
    # 전체 합계 출력
    print("\n전체 합계")
    print("=" * 50)
    total_df = pd.DataFrame(list(total_counts.items()), columns=['상품명', '수량'])
    total_df = total_df.sort_values('상품명')
    total_df['수량'] = total_df['수량'].astype(str) + '개'
    print(total_df.to_string(index=False))
    
    return total_df

def save_to_excel(product_counts):
    """
    상품 수량을 엑셀 파일로 저장합니다.
    """
    # 현재 날짜를 YYYYMMDD 형식으로 가져오기
    current_date = datetime.now().strftime("%Y%m%d")
    
    # 데이터프레임 생성
    df = pd.DataFrame(list(product_counts.items()), columns=['상품명', '수량'])
    
    # 수량으로 정렬
    df = df.sort_values('수량', ascending=False)
    
    # 엑셀 파일로 저장
    filename = f'상품집계_{current_date}.xlsx'
    df.to_excel(filename, index=False)
    print(f"\n집계 결과가 {filename}에 저장되었습니다.")
    return filename

def save_buyer_results_to_excel(buyer_product_counts):
    """
    구매자별 분석 결과를 엑셀 파일로 저장합니다.
    """
    try:
        # 현재 날짜를 YYYYMMDD 형식으로 가져오기
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f'구매자별_상품집계_{current_date}.xlsx'
        
        # 모든 데이터를 저장할 리스트
        all_data = []
        
        # 구매자별 데이터 추가
        for buyer, product_counts in buyer_product_counts.items():
            for product, count in product_counts.items():
                all_data.append({
                    '구매자': buyer,
                    '상품명': product,
                    '수량': count
                })
        
        # 전체 합계 계산
        total_counts = defaultdict(int)
        for product_counts in buyer_product_counts.values():
            for product, count in product_counts.items():
                total_counts[product] += count
        
        # 전체 합계 데이터 추가
        for product, count in total_counts.items():
            all_data.append({
                '구매자': '전체 합계',
                '상품명': product,
                '수량': count
            })
        
        # 데이터프레임 생성 및 저장
        df = pd.DataFrame(all_data)
        df = df.sort_values(['구매자', '수량'], ascending=[True, False])
        df.to_excel(filename, index=False)
        
        print(f"\n구매자별 집계 결과가 {filename}에 저장되었습니다.")
        return filename
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")
        return None

def main():
    """메인 프로그램"""
    print("쿠팡 주문서 분석기")
    print("=" * 50)
    print("1. 전체 상품 분석")
    print("2. 구매자별 상품 분석")
    print("=" * 50)

    choice = input("\n분석 방식을 선택하세요 (1 또는 2): ")
    file_path = input("\n엑셀 파일 경로를 입력하세요: ")
    
    if not os.path.exists(file_path):
        print("파일이 존재하지 않습니다.")
        return

    if choice == "1":
        # 기존 방식: 전체 상품 분석
        product_counts = analyze_excel_data(file_path)
        if product_counts:
            process_and_display_results(product_counts)
            save_to_excel(product_counts)
    elif choice == "2":
        # 새로운 방식: 구매자별 분석
        buyer_product_counts = analyze_excel_data_by_buyer(file_path)
        if buyer_product_counts:
            process_and_display_buyer_results(buyer_product_counts)
            save_buyer_results_to_excel(buyer_product_counts)
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()