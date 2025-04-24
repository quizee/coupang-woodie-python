import re
from collections import defaultdict

def normalize_product_name(name):
    if not isinstance(name, str):
        return name

    # 비건 올리브 치아바타 패턴
    if re.search(r'비건\s+올리브(\s+치아바타)?\s+\d+개입.*', name, re.IGNORECASE):
        return "올리브치아바타"

    # 우디베이크샵 패턴
    if "우디베이크샵" in name and "올리브" in name and "치아바타" in name:
        return "올리브치아바타"

    # 5가지맛 셋트 패턴
    if any(set_name in name for set_name in ["5가지맛 셋트", "5가지맛 세트", "5가지 맛 셋트", "5가지 맛 세트"]):
        return "5가지맛셋트"

    # 일반적인 치아바타 패턴
    for category in ["올리브", "치즈", "할라피뇨", "할리피뇨", "나폴리", "플레인"]:
        pattern = f"{category}\\s+치아바타"
        if re.search(pattern, name):
            name = re.sub(pattern, f"{category}치아바타", name)

    if "할리피뇨" in name:
        name = name.replace("할리피뇨", "할라피뇨")

    return name

def process_option(option, product_counts, quantity_multiplier=1):
    if not isinstance(option, str):
        return

    print("\n처리중인 옵션:", option)
    option = normalize_product_name(option)
    print("정규화된 옵션:", option)
    
    parts = option.split(',', 1)
    product_name = parts[0].strip()
    quantity_info = parts[1].strip() if len(parts) > 1 else ""
    print(f"상품명: {product_name}")
    print(f"수량 정보: {quantity_info}")

    # 구매 수량 추출 (기본값 1)
    purchase_quantity = 1
    quantity_match = re.search(r'(\d+)개(?!\s*입)', quantity_info)
    if quantity_match:
        purchase_quantity = int(quantity_match.group(1))
    print(f"구매 수량: {purchase_quantity}")

    # 5가지맛셋트 처리
    if "5가지맛셋트" in product_name:
        print("5가지맛셋트 처리:")
        for flavor in ["플레인치아바타", "올리브치아바타", "치즈치아바타", "할라피뇨치아바타", "나폴리치아바타"]:
            product_counts[flavor] += 1 * purchase_quantity
            print(f"  - {flavor} +{1 * purchase_quantity}개 추가")
        return

    # "치아바타 10개입 세트,10개 올리브치아바타 10개입" 패턴 처리
    if "세트" in product_name and "올리브치아바타" in quantity_info:
        print("세트 패턴 처리:")
        match = re.search(r'(\d+)개입', quantity_info)
        if match:
            quantity = int(match.group(1))
            product_counts["올리브치아바타"] += quantity * purchase_quantity
            print(f"  - 올리브치아바타 +{quantity * purchase_quantity}개 추가")
            return

    # "비건 올리브 치아바타 5개입" 패턴 처리
    if "비건 올리브 치아바타" in product_name:
        print("비건 올리브 치아바타 패턴 처리:")
        match = re.search(r'(\d+)개입', product_name)
        if match:
            quantity = int(match.group(1))
            product_counts["올리브치아바타"] += quantity * purchase_quantity
            print(f"  - 올리브치아바타 +{quantity * purchase_quantity}개 추가")
            return

    # "우디베이크샵 비건 치아바타 올리브" 패턴 처리
    if "우디베이크샵" in product_name and "올리브" in product_name and "치아바타" in product_name:
        print("우디베이크샵 패턴 처리:")
        product_counts["올리브치아바타"] += 1 * purchase_quantity
        print(f"  - 올리브치아바타 +{1 * purchase_quantity}개 추가")
        return

def analyze_text_data(text):
    product_counts = defaultdict(int)
    print("\n=== 텍스트 분석 시작 ===")

    # 각 줄을 직접 처리
    lines = text.strip().split('\n')
    for line in lines:
        print(f"\n처리중인 줄: {line}")
        process_option(line, product_counts)

    print("\n=== 최종 집계 결과 ===")
    for product, count in sorted(product_counts.items()):
        print(f"{product}: {count}개")

    return product_counts

# 테스트 데이터
test_data = '''치아바타 10개입 세트,10개 올리브치아바타 10개입
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
5가지맛 셋트,120g 5개
치아바타 10개입 세트,10개 올리브치아바타 10개입
비건 올리브 치아바타 5개입 가성비 고정품,100g 5개
치아바타 10개입 세트,10개 올리브치아바타 10개입
5가지맛 셋트,120g 5개
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
5가지맛 셋트,120g 5개
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
치아바타 10개입 세트,10개 올리브치아바타 10개입
5가지맛 셋트,120g 5개
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
치아바타 10개입 세트,10개 올리브치아바타 10개입
비건 올리브 치아바타 5개입 가성비 고정품,100g 5개
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
5가지맛 셋트,120g 5개
5가지맛 셋트,120g 5개
비건 올리브 치아바타 5개입 가성비 고정품,100g 5개
치아바타 10개입 세트,10개 올리브치아바타 10개입
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타
치아바타 10개입 세트,10개 올리브치아바타 10개입
우디베이크샵 비건 치아바타 올리브 치즈 할라피뇨 건강빵 (여성용 발부제 무첨가),100g 1개 올리브 치아바타'''

analyze_text_data(test_data)

def test_counting():
    # 테스트 케이스들
    test_cases = [
        # 케이스 1: "상품명,10개 올리브치아바타 10개입"
        "비건 올리브 치아바타 5개입 가성비 굿상품,10개 올리브치아바타 10개입",
        
        # 케이스 2: "상품명,1개"
        "비건 올리브 치아바타 5개입 가성비 굿상품,1개",
        
        # 케이스 3: "상품명,100g 3개"
        "비건 올리브 치아바타 5개입 가성비 굿상품,100g 3개",
        
        # 케이스 4: "상품명,올리브치아바타 5개 + 치즈치아바타 5개"
        "비건 올리브 치아바타 5개입 가성비 굿상품,올리브치아바타 5개 + 치즈치아바타 5개",
        
        # 케이스 5: "상품명,100g 1개 옵션명"
        "비건 올리브 치아바타 5개입 가성비 굿상품,100g 1개 호두초코쿠키",
        "비건 올리브 치아바타 5개입 가성비 굿상품,100g 1개 올리브 치아바타"
    ]
    
    # 결과를 저장할 딕셔너리
    product_counts = defaultdict(int)
    
    # 각 테스트 케이스 실행
    for test_case in test_cases:
        print("\n" + "="*50)
        print(f"테스트 케이스: {test_case}")
        print("="*50)
        process_option(test_case, product_counts)
    
    # 최종 결과 출력
    print("\n" + "="*50)
    print("최종 결과:")
    print("="*50)
    for product, count in sorted(product_counts.items()):
        print(f"{product}: {count}개")

if __name__ == "__main__":
    test_counting() 