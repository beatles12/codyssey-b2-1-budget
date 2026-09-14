import csv
from datetime import datetime
from pathlib import Path

from budget_app.repository import (
    CategoryRepository,
    TransactionRepository,
)
from budget_app.service import TransactionService


# ==========================================================
# [1] CSV에서 사용하는 열 이름
# ==========================================================
# 공식 CSV 최소 스키마:
#
# date,type,category,amount,memo,tags
# ==========================================================

CSV_FIELDNAMES = [
    "date",
    "type",
    "category",
    "amount",
    "memo",
    "tags",
]


# ==========================================================
# [2] CSV 서비스 클래스
# ==========================================================
# 역할:
# - 거래를 CSV 파일로 내보냄(export)
# - CSV 파일의 거래를 프로그램으로 가져옴(import)
# ==========================================================

class CsvService:

    # ======================================================
    # [2-1] CSV 서비스 초기화
    # ======================================================

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
    ) -> None:

        self.transaction_repository = (
            transaction_repository
        )

        self.category_repository = (
            category_repository
        )

        # 거래 추가 시 기존 TransactionService의
        # 검증과 UUID 생성 기능을 그대로 재사용함
        self.transaction_service = (
            TransactionService(
                transaction_repository
            )
        )


    # ======================================================
    # [3] 월 형식 검사
    # ======================================================

    def _validate_month(
        self,
        month: str,
    ) -> None:

        try:
            datetime.strptime(
                month,
                "%Y-%m",
            )

        except ValueError as error:

            raise ValueError(
                "월은 YYYY-MM 형식이어야 합니다."
            ) from error


    # ======================================================
    # [4] 날짜 형식 검사
    # ======================================================

    def _validate_date(
        self,
        date: str,
    ) -> None:

        try:
            datetime.strptime(
                date,
                "%Y-%m-%d",
            )

        except ValueError as error:

            raise ValueError(
                "날짜는 YYYY-MM-DD 형식이어야 합니다."
            ) from error


    # ======================================================
    # [5] CSV 내보내기
    # ======================================================

    def export_transactions(
        self,
        out_path: str,
        month: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> int:

        if month:

            self._validate_month(
                month
            )

            if date_from or date_to:

                raise ValueError(
                    "--month와 --from/--to는 "
                    "동시에 사용할 수 없습니다."
                )

        else:

            if not date_from or not date_to:

                raise ValueError(
                    "--month 또는 "
                    "--from과 --to를 입력해야 합니다."
                )

            self._validate_date(
                date_from
            )

            self._validate_date(
                date_to
            )

            if date_from > date_to:

                raise ValueError(
                    "시작 날짜는 끝 날짜보다 "
                    "늦을 수 없습니다."
                )


        output_file = Path(
            out_path
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        exported_count = 0


        with output_file.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CSV_FIELDNAMES,
            )

            writer.writeheader()


            for transaction in (
                self.transaction_repository.iter_transactions()
            ):

                if month:

                    if not transaction.date.startswith(
                        month
                    ):
                        continue

                else:

                    if transaction.date < date_from:
                        continue

                    if transaction.date > date_to:
                        continue


                tags_text = ",".join(
                    transaction.tags
                )


                writer.writerow(
                    {
                        "date": transaction.date,
                        "type": transaction.type,
                        "category": transaction.category,
                        "amount": transaction.amount,
                        "memo": transaction.memo,
                        "tags": tags_text,
                    }
                )

                exported_count += 1


        return exported_count


    # ======================================================
    # [6] CSV 가져오기
    # ======================================================
    # 반환값:
    #
    # imported_count
    # = 정상적으로 등록된 거래 수
    #
    # skipped_count
    # = 잘못된 값이라 건너뛴 거래 수
    #
    # 예:
    # (5, 1)
    #
    # → 5건 등록
    # → 1건 건너뜀
    # ==========================================================

    def import_transactions(
        self,
        from_path: str,
    ) -> tuple[int, int]:

        input_file = Path(
            from_path
        )


        # ----------------------------------------------
        # CSV 파일 존재 여부 확인
        # ----------------------------------------------

        if not input_file.exists():

            raise ValueError(
                f"CSV 파일을 찾을 수 없습니다: "
                f"{from_path}"
            )


        imported_count = 0
        skipped_count = 0


        # ----------------------------------------------
        # CSV 파일 열기
        # ----------------------------------------------

        with input_file.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.DictReader(
                file
            )


            # ------------------------------------------
            # CSV 헤더 검사
            # ------------------------------------------

            if reader.fieldnames is None:

                raise ValueError(
                    "CSV 헤더가 없습니다."
                )


            missing_columns = [
                field
                for field in CSV_FIELDNAMES
                if field not in reader.fieldnames
            ]


            if missing_columns:

                raise ValueError(
                    "CSV 필수 열이 없습니다: "
                    + ", ".join(missing_columns)
                )


            # ------------------------------------------
            # 거래 한 줄씩 처리
            # ------------------------------------------

            for row in reader:

                try:

                    date = (
                        row["date"].strip()
                    )

                    transaction_type = (
                        row["type"].strip()
                    )

                    category = (
                        row["category"].strip()
                    )

                    amount_text = (
                        row["amount"].strip()
                    )

                    memo = (
                        row.get(
                            "memo",
                            ""
                        )
                        or ""
                    ).strip()

                    tags_text = (
                        row.get(
                            "tags",
                            ""
                        )
                        or ""
                    ).strip()


                    # ----------------------------------
                    # 금액을 문자열 → 정수로 변환
                    # ----------------------------------

                    amount = int(
                        amount_text
                    )


                    # ----------------------------------
                    # 등록되지 않은 카테고리 검사
                    # ----------------------------------

                    if not self.category_repository.exists(
                        category
                    ):

                        raise ValueError(
                            "등록되지 않은 카테고리입니다."
                        )


                    # ----------------------------------
                    # 태그 문자열 → 리스트
                    #
                    # "meal,dinner"
                    #       ↓
                    # ["meal", "dinner"]
                    # ----------------------------------

                    if tags_text:

                        tags = [
                            tag.strip()
                            for tag in tags_text.split(",")
                            if tag.strip()
                        ]

                    else:

                        tags = []


                    # ----------------------------------
                    # 기존 TransactionService 재사용
                    #
                    # 여기서:
                    # - 날짜 검사
                    # - income/expense 검사
                    # - 양수 금액 검사
                    # - UUID 생성
                    # - JSONL 저장
                    # 모두 처리됨
                    # ----------------------------------

                    self.transaction_service.add_transaction(
                        transaction_type=transaction_type,
                        date=date,
                        amount=amount,
                        category=category,
                        memo=memo,
                        tags=tags,
                    )


                    imported_count += 1


                # --------------------------------------
                # 한 줄이 잘못되어도
                # 전체 import는 멈추지 않고
                # 그 줄만 건너뜀
                # --------------------------------------

                except (
                    ValueError,
                    TypeError,
                    KeyError,
                ):

                    skipped_count += 1


        return (
            imported_count,
            skipped_count,
        )