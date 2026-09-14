import json
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path

from budget_app.models import Transaction


# ==========================================================
# [1] 거래 저장소 클래스
# ==========================================================
# 역할:
# - 거래 데이터를 JSONL 파일에 저장하고 다시 불러옴
# - 거래 수정과 삭제처럼 파일 내용을 바꾸는 작업도 담당함
# ==========================================================

class TransactionRepository:

    # ======================================================
    # [1-1] 거래 저장소 초기화
    # ======================================================

    def __init__(
        self,
        file_path: str = "data/transactions.jsonl"
    ) -> None:

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    # ======================================================
    # [2] 거래 한 건 저장
    # ======================================================

    def add(
        self,
        transaction: Transaction
    ) -> None:

        with self.file_path.open(
            "a",
            encoding="utf-8"
        ) as file:

            json.dump(
                asdict(transaction),
                file,
                ensure_ascii=False
            )

            file.write("\n")


    # ======================================================
    # [3] 저장된 거래 한 건씩 읽기
    # ======================================================
    # yield를 이용해 파일 전체를 한꺼번에 읽지 않고
    # 거래를 한 건씩 반환함
    # ======================================================

    def iter_transactions(
        self
    ) -> Iterator[Transaction]:

        if not self.file_path.exists():
            return

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                data = json.loads(line)

                yield Transaction(
                    id=data["id"],
                    type=data["type"],
                    date=data["date"],
                    amount=data["amount"],
                    category=data["category"],
                    memo=data.get("memo", ""),
                    tags=data.get("tags", []),
                )


    # ======================================================
    # [4] ID로 거래 한 건 찾기
    # ======================================================
    # 찾으면 Transaction 객체 반환
    # 없으면 None 반환
    # ======================================================

    def find_by_id(
        self,
        transaction_id: str
    ) -> Transaction | None:

        for transaction in self.iter_transactions():

            if transaction.id == transaction_id:
                return transaction

        return None


    # ======================================================
    # [5] ID로 거래 수정
    # ======================================================
    # JSONL 파일 중간의 한 줄만 직접 바꾸지 않고
    # 임시 파일을 만들어 안전하게 전체를 다시 작성함
    #
    # 수정 대상 id를 만나면
    # 기존 거래 대신 updated_transaction을 저장함
    #
    # 수정 성공 = True
    # 없는 id   = False
    # ======================================================

    def update_by_id(
        self,
        transaction_id: str,
        updated_transaction: Transaction,
    ) -> bool:

        temp_path = self.file_path.with_suffix(
            ".tmp"
        )

        found = False

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as temp_file:

            for transaction in self.iter_transactions():

                # 수정할 거래를 발견한 경우
                if transaction.id == transaction_id:

                    json.dump(
                        asdict(updated_transaction),
                        temp_file,
                        ensure_ascii=False
                    )

                    temp_file.write("\n")

                    found = True
                    continue

                # 수정 대상이 아닌 거래는 그대로 다시 저장
                json.dump(
                    asdict(transaction),
                    temp_file,
                    ensure_ascii=False
                )

                temp_file.write("\n")

        # 수정할 거래가 존재했다면
        # 완성된 임시 파일로 원본 파일 교체
        if found:

            temp_path.replace(
                self.file_path
            )

            return True

        # 없는 id라면 원본은 그대로 두고
        # 임시 파일만 삭제
        temp_path.unlink(
            missing_ok=True
        )

        return False


    # ======================================================
    # [6] ID로 거래 삭제
    # ======================================================
    # 삭제할 거래만 제외하고 임시 파일에 다시 저장한 뒤
    # 기존 파일과 교체함
    #
    # 삭제 성공 = True
    # 없는 id   = False
    # ======================================================

    def delete_by_id(
        self,
        transaction_id: str
    ) -> bool:

        temp_path = self.file_path.with_suffix(
            ".tmp"
        )

        found = False

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as temp_file:

            for transaction in self.iter_transactions():

                if transaction.id == transaction_id:

                    found = True
                    continue

                json.dump(
                    asdict(transaction),
                    temp_file,
                    ensure_ascii=False
                )

                temp_file.write("\n")

        if found:

            temp_path.replace(
                self.file_path
            )

            return True

        temp_path.unlink(
            missing_ok=True
        )

        return False


# ==========================================================
# [7] 카테고리 저장소 클래스
# ==========================================================
# 역할:
# - 사용할 수 있는 카테고리 목록을 JSONL 파일로 관리함
# ==========================================================

class CategoryRepository:

    DEFAULT_CATEGORIES = [
        "food",
        "coffee",
        "transport",
        "shopping",
        "housing",
        "health",
        "education",
        "salary",
        "etc",
    ]


    # ======================================================
    # [7-1] 카테고리 저장소 초기화
    # ======================================================

    def __init__(
        self,
        file_path: str = "data/categories.jsonl"
    ) -> None:

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if (
            not self.file_path.exists()
            or self.file_path.stat().st_size == 0
        ):
            self._create_default_categories()


    # ======================================================
    # [8] 기본 카테고리 자동 생성
    # ======================================================

    def _create_default_categories(
        self
    ) -> None:

        with self.file_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            for category in self.DEFAULT_CATEGORIES:

                json.dump(
                    {"name": category},
                    file,
                    ensure_ascii=False
                )

                file.write("\n")


    # ======================================================
    # [9] 카테고리 한 건씩 읽기
    # ======================================================

    def iter_categories(
        self
    ) -> Iterator[str]:

        if not self.file_path.exists():
            return

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                data = json.loads(line)

                yield data["name"]


    # ======================================================
    # [10] 카테고리 존재 여부 확인
    # ======================================================

    def exists(
        self,
        category_name: str
    ) -> bool:

        for category in self.iter_categories():

            if category == category_name:
                return True

        return False


    # ======================================================
    # [11] 새 카테고리 추가
    # ======================================================

    def add(
        self,
        category_name: str
    ) -> None:

        with self.file_path.open(
            "a",
            encoding="utf-8"
        ) as file:

            json.dump(
                {"name": category_name},
                file,
                ensure_ascii=False
            )

            file.write("\n")


    # ======================================================
    # [12] 카테고리 삭제
    # ======================================================

    def remove(
        self,
        category_name: str
    ) -> bool:

        categories = list(
            self.iter_categories()
        )

        if category_name not in categories:
            return False

        remaining_categories = [
            category
            for category in categories
            if category != category_name
        ]

        with self.file_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            for category in remaining_categories:

                json.dump(
                    {"name": category},
                    file,
                    ensure_ascii=False
                )

                file.write("\n")

        return True