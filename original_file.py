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
    if re.search(r"비건\s+올리브(\s+치아바타)?\s+\d+개입.*", name, re.IGNORECASE):
        return "올리브치아바타"

    # 우디베이크샵 매콤 할라피뇨 치아바타 -> 할라피뇨치아바타 통일
    if re.search(r"우디베이크샵.*할라피뇨.*치아바타", name, re.IGNORECASE):
        return "할라피뇨치아바타"

    # 5가지맛 셋트 -> 5가지맛셋트 통일
    if any(
        set_name in name
        for set_name in [
            "5가지맛 셋트",
            "5가지맛 세트",
            "5가지 맛 셋트",
            "5가지 맛 세트",
        ]
    ):
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


def process_option(
    option, product_counts, quantity_multiplier=1, is_buyer_analysis=False
):
    """
    개별 옵션 정보를 처리하여 상품명과 수량을 추출합니다.
    """
    if not isinstance(option, str):
        return

    print("\n처리중인 옵션:", option)

    # 쉼표로 분리
    parts = option.split(",", 1)
    if len(parts) < 2:
        print("쉼표가 없는 옵션은 무시합니다.")
        return

    product_name = parts[0].strip()
    quantity_info = parts[1].strip()

    # '-' 기호 제거
    quantity_info = quantity_info.replace("-", "").strip()

    print(f"상품명: {product_name}")
    print(f"수량 정보: {quantity_info}")
    print(f"구매 수량 배수: {quantity_multiplier}")

    # 특별 케이스 1: 5가지맛 셋트
    if "5가지맛 셋트" in product_name or "5가지맛 세트" in product_name:
        print("5가지맛셋트 처리:")
        for flavor in [
            "플레인치아바타",
            "올리브치아바타",
            "치즈치아바타",
            "할라피뇨치아바타",
            "나폴리치아바타",
        ]:
            product_counts[flavor] += quantity_multiplier
            print(f"  - {flavor} +{quantity_multiplier}개 추가")
        return

    # 치아바타 10개입 세트인 경우
    if "치아바타 10개입 세트" in product_name:
        if is_buyer_analysis:
            # 수취인별 분석일 때는 전체 옵션을 상품명으로 사용
            print("치아바타 10개입 세트 처리 (수취인별 분석):")
            product_counts[option] += quantity_multiplier
            print(f"  - {option} +{quantity_multiplier}개 추가")
        else:
            # 케이스 1: "10개 올리브치아바타 10개입" -> 치아바타 종류별 처리
            chiabatta_pattern = r"(\d+)개\s+([가-힣]+)(?:\s*치아바타)"
            chiabatta_matches = re.findall(chiabatta_pattern, quantity_info)
            if chiabatta_matches:
                print("치아바타 종류별 처리:")
                for quantity, chiabatta_type in chiabatta_matches:
                    normalized_name = (
                        f"{normalize_product_name(chiabatta_type)}치아바타"
                    )
                    product_counts[normalized_name] += (
                        int(quantity) * quantity_multiplier
                    )
                    print(
                        f"  - {normalized_name} +{int(quantity) * quantity_multiplier}개 추가"
                    )
                return
            # 케이스 4: "올리브치아바타 5개 + 치즈치아바타 5개" -> 치아바타 종류별 처리
            if "+" in quantity_info:
                print("치아바타 조합 패턴 처리:")
                chiabatta_pattern = r"([가-힣]+)(?:\s*치아바타)\s*(\d+)개"
                chiabatta_matches = re.findall(chiabatta_pattern, quantity_info)
                if chiabatta_matches:
                    for chiabatta_type, quantity in chiabatta_matches:
                        normalized_name = (
                            f"{normalize_product_name(chiabatta_type)}치아바타"
                        )
                        product_counts[normalized_name] += (
                            int(quantity) * quantity_multiplier
                        )
                        print(
                            f"  - {normalized_name} +{int(quantity) * quantity_multiplier}개 추가"
                        )
                    return
        return

    # 상품명 정규화
    product_name = normalize_product_name(product_name)

    # 케이스 5: "100g 1개 옵션명" -> 옵션명 추출
    option_name_match = re.search(
        r"\d+개\s+([가-힣]+(?:\s*치아바타)?(?:\s*쿠키)?)", quantity_info
    )
    if option_name_match:
        print("옵션명 처리:")
        option_name = normalize_product_name(option_name_match.group(1))
        product_counts[option_name] += quantity_multiplier
        print(f"  - {option_name} +{quantity_multiplier}개 추가")
        return

    # 케이스 2 & 3: "1개" 또는 "100g 3개" -> 수량 추출
    quantity_match = re.search(r"(\d+)개(?!\s*입)", quantity_info)
    if quantity_match:
        print("일반 수량 패턴 처리:")
        quantity = int(quantity_match.group(1))
        product_counts[product_name] += quantity * quantity_multiplier
        print(f"  - {product_name} +{quantity * quantity_multiplier}개 추가")
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
    comma_count = text.count(",")
    line_count = text.count("\n") + 1

    if (
        comma_count > line_count * 0.3
    ):  # 30% 이상의 줄에 쉼표가 있으면 쿠팡 형식으로 간주
        # 쿠팡 엑셀 내보내기 형식 처리
        # 각 줄 처리
        lines = text.strip().split("\n")

        # 옵션명이 포함된 필드 찾기
        for line in lines:
            # 쉼표가 포함된 필드 찾기
            fields = line.split()
            for field in fields:
                if "," in field:
                    # 올바른 형식인지 확인 (상품명,수량)
                    if re.search(r".+,.+", field):
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
                option = (
                    row[option_column_name]
                    if not pd.isna(row[option_column_name])
                    else ""
                )

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
                    if isinstance(value, str) and "," in value:
                        # 올바른 형식인지 확인
                        if re.search(r".+,.+", value):
                            process_option(value, product_counts)

        return product_counts

    except Exception as e:
        print(f"엑셀 파일 분석 중 오류 발생: {str(e)}")
        return None


def analyze_excel_data_by_buyer(file_path):
    """
    엑셀 파일을 읽어서 수취인별로 주문 정보를 분석합니다.
    """
    try:
        df = pd.read_excel(file_path)
        print("엑셀 파일을 성공적으로 읽었습니다.")
    except Exception as e:
        print(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

    # 필수 열이 있는지 확인
    required_columns = [
        "수취인이름",
        "수취인전화번호",
        "수취인 주소",
        "최초등록등록상품명/옵션명",
        "구매수(수량)",
        "주문일",
    ]
    if not all(col in df.columns for col in required_columns):
        print("필수 열이 없습니다. 파일 형식을 확인해주세요.")
        return None

    # 수취인별 상품 개수를 저장할 딕셔너리
    buyer_product_counts = {}
    # 수취인 정보를 저장할 딕셔너리 (주소별로 이름과 전화번호, 주문일 매핑)
    buyer_info = {}

    # 각 행을 순회하면서 처리
    for _, row in df.iterrows():
        buyer_name = str(row["수취인이름"]).strip()
        buyer_phone = str(row["수취인전화번호"]).strip()
        buyer_address = str(row["수취인 주소"]).strip()
        options = str(row["최초등록등록상품명/옵션명"]).strip()
        quantity_multiplier = int(row["구매수(수량)"])
        order_date = pd.to_datetime(row["주문일"]).strftime("%Y-%m-%d %H:%M:%S")

        # 수취인 주소를 키로 사용
        buyer_key = buyer_address

        # 새로운 수취인이면 딕셔너리 초기화
        if buyer_key not in buyer_product_counts:
            buyer_product_counts[buyer_key] = defaultdict(int)
            buyer_info[buyer_key] = {
                "name": buyer_name,
                "phone": buyer_phone,
                "order_date": order_date,
            }
        else:
            # 기존 수취인의 경우 더 빠른 주문일로 업데이트
            current_date = buyer_info[buyer_key]["order_date"]
            if order_date < current_date:
                buyer_info[buyer_key]["order_date"] = order_date

        # 옵션 정보가 여러 줄일 경우 각각 처리
        for option in options.split("\n"):
            if isinstance(option, str) and option:
                process_option(
                    option, buyer_product_counts[buyer_key], quantity_multiplier, True
                )

    return buyer_product_counts, buyer_info


def process_and_display_results(product_counts, title="쿠팡 주문 분석 결과"):
    """
    분석 결과를 처리하고 화면에 표시합니다.
    """
    if not product_counts:
        return None

    # 결과를 데이터프레임으로 변환
    df = pd.DataFrame(list(product_counts.items()), columns=["상품명", "수량"])
    df = df.sort_values("상품명")  # 상품명으로 정렬
    df["수량"] = df["수량"].astype(str) + "개"

    # 결과 출력
    print(f"\n{title}")
    print("=" * 50)
    print(df.to_string(index=False))
    print("=" * 50)

    # CSV 파일로 저장
    output_filename = "쿠팡주문분석결과.csv"
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"\n분석 결과가 {output_filename} 파일로 저장되었습니다.")

    return df


def process_and_display_buyer_results(buyer_product_counts, buyer_info):
    """
    구매자별 분석 결과를 처리하고 표시합니다.
    """
    if not buyer_product_counts:
        print("분석할 데이터가 없습니다.")
        return

    # 결과를 저장할 리스트
    results = []

    # 각 구매자별로 처리
    for buyer_key, products in buyer_product_counts.items():
        # 구매자 정보 가져오기
        buyer_name = buyer_info[buyer_key]["name"]
        buyer_phone = buyer_info[buyer_key]["phone"]
        buyer_address = buyer_key  # 주소가 키로 사용됨

        # 주문내역 문자열 생성
        order_details = []
        for product, count in sorted(products.items()):
            order_details.append(f"{product} {count}개")
        order_text = " / ".join(order_details)

        # 결과 추가
        results.append(
            {
                "수취인이름": buyer_name,
                "수취인전화번호": buyer_phone,
                "수취인 주소": buyer_address,
                "주문건": order_text,
            }
        )

    # 주문건 기준으로 정렬
    results.sort(key=lambda x: x["주문건"], reverse=True)

    # 결과를 엑셀 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"구매자별_주문분석_{timestamp}.xlsx"

    try:
        df = pd.DataFrame(results)
        df.to_excel(excel_filename, index=False, engine="openpyxl")
        print(f"\n분석 결과가 {excel_filename} 파일로 저장되었습니다.")
    except Exception as e:
        print(f"엑셀 파일 저장 중 오류 발생: {e}")


def save_to_excel(product_counts):
    """
    상품 수량을 엑셀 파일로 저장합니다.
    """
    # 현재 날짜를 YYYYMMDD 형식으로 가져오기
    current_date = datetime.now().strftime("%Y%m%d")

    # 데이터프레임 생성
    df = pd.DataFrame(list(product_counts.items()), columns=["상품명", "수량"])

    # 수량으로 정렬
    df = df.sort_values("수량", ascending=False)

    # 엑셀 파일로 저장
    filename = f"상품집계_{current_date}.xlsx"
    df.to_excel(filename, index=False)
    print(f"\n집계 결과가 {filename}에 저장되었습니다.")
    return filename


def save_buyer_results_to_excel(buyer_product_counts, buyer_info):
    """
    구매자별 분석 결과를 엑셀 파일로 저장합니다.
    """
    if not buyer_product_counts:
        return

    # 결과를 저장할 리스트
    results = []

    # 각 구매자별로 처리
    for buyer_key, products in buyer_product_counts.items():
        # 구매자 정보 가져오기
        buyer_name = buyer_info[buyer_key]["name"]
        buyer_phone = buyer_info[buyer_key]["phone"]
        buyer_address = buyer_key  # 주소가 키로 사용됨
        order_date = buyer_info[buyer_key]["order_date"]

        # 주문내역 문자열 생성
        order_details = []
        for product, count in sorted(products.items()):
            order_details.append(f"{product} {count}개")
        order_text = " / ".join(order_details)

        # 결과 추가
        results.append(
            {
                "수취인이름": buyer_name,
                "수취인전화번호": buyer_phone,
                "수취인 주소": buyer_address,
                "주문건": order_text,
                "주문일": order_date,
            }
        )

    # 주문일 기준으로 정렬
    results.sort(key=lambda x: x["주문일"])

    # 결과를 엑셀 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"구매자별_주문분석_{timestamp}.xlsx"

    try:
        df = pd.DataFrame(results)
        # 주문일 컬럼 제거 (표시용으로만 사용)
        df = df[["수취인이름", "수취인전화번호", "수취인 주소", "주문건"]]
        df.to_excel(excel_filename, index=False, engine="openpyxl")
        print(f"\n분석 결과가 {excel_filename} 파일로 저장되었습니다.")
    except Exception as e:
        print(f"엑셀 파일 저장 중 오류 발생: {e}")


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
        buyer_product_counts, buyer_info = analyze_excel_data_by_buyer(file_path)
        if buyer_product_counts:
            process_and_display_buyer_results(buyer_product_counts, buyer_info)
            save_buyer_results_to_excel(buyer_product_counts, buyer_info)
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
