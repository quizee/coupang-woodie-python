import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt
import pandas as pd
from original_file import (
    analyze_excel_data,
    process_and_display_results,
    analyze_excel_data_by_buyer,
    process_and_display_buyer_results,
)
from datetime import datetime


class CoupangAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.product_counts = None  # 분석 결과를 저장할 변수 추가
        self.buyer_product_counts = None  # 구매자별 분석 결과를 저장할 변수 추가

    def initUI(self):
        self.setWindowTitle("쿠팡 주문서 분석기")
        self.setGeometry(100, 100, 800, 600)

        # 메인 위젯과 레이아웃 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 분석 방식 선택
        analysis_layout = QHBoxLayout()
        self.analysis_group = QButtonGroup()

        self.total_radio = QRadioButton("전체 상품 분석")
        self.buyer_radio = QRadioButton("수취인별 분석")
        self.total_radio.setChecked(True)  # 기본값으로 전체 상품 분석 선택

        self.analysis_group.addButton(self.total_radio)
        self.analysis_group.addButton(self.buyer_radio)

        analysis_layout.addWidget(self.total_radio)
        analysis_layout.addWidget(self.buyer_radio)
        layout.addLayout(analysis_layout)

        # 파일 선택 버튼
        file_layout = QHBoxLayout()
        self.file_label = QLabel("선택된 파일: 없음")
        self.select_file_btn = QPushButton("엑셀 파일 선택")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_file_btn)
        layout.addLayout(file_layout)

        # 분석 버튼
        self.analyze_btn = QPushButton("분석하기")
        self.analyze_btn.clicked.connect(self.analyze_file)
        self.analyze_btn.setEnabled(False)
        layout.addWidget(self.analyze_btn)

        # 결과 테이블
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)  # 기본적으로 2개 컬럼 (상품명, 수량)
        self.result_table.setHorizontalHeaderLabels(["상품명", "수량"])
        self.result_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.result_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        layout.addWidget(self.result_table)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 엑셀 다운로드 버튼
        self.excel_download_btn = QPushButton("엑셀 다운로드")
        self.excel_download_btn.clicked.connect(self.download_excel)
        self.excel_download_btn.setEnabled(False)
        button_layout.addWidget(self.excel_download_btn)

        layout.addLayout(button_layout)

        # 상태 표시 레이블
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.selected_file = None

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_name:
            self.selected_file = file_name
            self.file_label.setText(f"선택된 파일: {os.path.basename(file_name)}")
            self.analyze_btn.setEnabled(True)

    def analyze_file(self):
        if not self.selected_file:
            return

        try:
            # 테이블 초기화
            self.result_table.setRowCount(0)

            if self.total_radio.isChecked():
                # 전체 상품 분석
                self.product_counts = analyze_excel_data(self.selected_file)
                if self.product_counts:
                    # 테이블 컬럼 설정
                    self.result_table.setColumnCount(2)
                    self.result_table.setHorizontalHeaderLabels(["상품명", "수량"])

                    # 결과를 테이블에 표시
                    for product, count in sorted(self.product_counts.items()):
                        row_position = self.result_table.rowCount()
                        self.result_table.insertRow(row_position)
                        self.result_table.setItem(
                            row_position, 0, QTableWidgetItem(product)
                        )
                        self.result_table.setItem(
                            row_position, 1, QTableWidgetItem(f"{count}개")
                        )

                    self.status_label.setText("분석이 완료되었습니다.")
                    self.excel_download_btn.setEnabled(True)
                else:
                    self.status_label.setText("분석 중 오류가 발생했습니다.")
                    self.excel_download_btn.setEnabled(False)
            else:
                # 구매자별 분석
                self.buyer_product_counts, self.buyer_info = (
                    analyze_excel_data_by_buyer(self.selected_file)
                )
                if self.buyer_product_counts:
                    # 테이블 컬럼 설정
                    self.result_table.setColumnCount(4)
                    self.result_table.setHorizontalHeaderLabels(
                        ["수취인이름", "수취인전화번호", "수취인 주소", "주문건"]
                    )

                    # 결과를 테이블에 표시
                    for buyer_key, product_counts in self.buyer_product_counts.items():
                        row_position = self.result_table.rowCount()
                        self.result_table.insertRow(row_position)

                        # 구매자 정보 가져오기
                        buyer_name = self.buyer_info[buyer_key]["name"]
                        buyer_phone = self.buyer_info[buyer_key]["phone"]
                        buyer_address = buyer_key  # 주소가 키로 사용됨

                        # 주문내역 문자열 생성
                        order_details = []
                        for product, count in sorted(product_counts.items()):
                            order_details.append(f"{product} {count}개")
                        order_text = " / ".join(order_details)

                        self.result_table.setItem(
                            row_position, 0, QTableWidgetItem(buyer_name)
                        )
                        self.result_table.setItem(
                            row_position, 1, QTableWidgetItem(buyer_phone)
                        )
                        self.result_table.setItem(
                            row_position, 2, QTableWidgetItem(buyer_address)
                        )
                        self.result_table.setItem(
                            row_position, 3, QTableWidgetItem(order_text)
                        )

                    self.status_label.setText("분석이 완료되었습니다.")
                    self.excel_download_btn.setEnabled(True)
                else:
                    self.status_label.setText("분석 중 오류가 발생했습니다.")
                    self.excel_download_btn.setEnabled(False)

        except Exception as e:
            self.status_label.setText(f"오류 발생: {str(e)}")
            self.excel_download_btn.setEnabled(False)

    def download_excel(self):
        try:
            # 현재 날짜를 파일명에 포함
            current_date = datetime.now().strftime("%Y%m%d")

            if self.total_radio.isChecked():
                # 전체 상품 분석 결과 저장
                default_filename = f"상품집계_{current_date}.xlsx"
                file_name, _ = QFileDialog.getSaveFileName(
                    self, "엑셀 파일 저장", default_filename, "Excel Files (*.xlsx)"
                )

                if file_name and self.product_counts:
                    df = pd.DataFrame(
                        list(self.product_counts.items()), columns=["상품명", "수량"]
                    )
                    df = df.sort_values("수량", ascending=False)
                    df["수량"] = df["수량"].astype(str) + "개"
                    df.to_excel(file_name, index=False)
            else:
                # 구매자별 분석 결과 저장
                default_filename = f"구매자별_상품집계_{current_date}.xlsx"
                file_name, _ = QFileDialog.getSaveFileName(
                    self, "엑셀 파일 저장", default_filename, "Excel Files (*.xlsx)"
                )

                if file_name and self.buyer_product_counts:
                    all_data = []
                    for buyer_key, product_counts in self.buyer_product_counts.items():
                        # 구매자 정보 가져오기
                        buyer_name = self.buyer_info[buyer_key]["name"]
                        buyer_phone = self.buyer_info[buyer_key]["phone"]
                        buyer_address = buyer_key  # 주소가 키로 사용됨

                        # 주문내역 문자열 생성
                        order_details = []
                        for product, count in sorted(product_counts.items()):
                            order_details.append(f"{product} {count}개")
                        order_text = " / ".join(order_details)

                        all_data.append(
                            {
                                "수취인이름": buyer_name,
                                "수취인전화번호": buyer_phone,
                                "수취인 주소": buyer_address,
                                "주문건": order_text,
                            }
                        )

                    df = pd.DataFrame(all_data)
                    df = df.sort_values("수취인이름")
                    df.to_excel(file_name, index=False)

            if file_name:
                self.status_label.setText(
                    f"엑셀 파일이 저장되었습니다: {os.path.basename(file_name)}"
                )

        except Exception as e:
            self.status_label.setText(f"엑셀 파일 저장 중 오류 발생: {str(e)}")


def main():
    app = QApplication(sys.argv)
    ex = CoupangAnalyzerGUI()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
