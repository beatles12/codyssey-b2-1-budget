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
# - 거래 삭제처럼 파일 내용을 변경하는 작업도 담당함
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
    # yield를 이용해 전체 파일을 한꺼번에 읽지 않고
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
    # 거래를 한 건씩 읽으면서
    # 요청한 id와 같은 거래를 찾음
    #
    # 찾으면 Transaction 반환
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
    # [5] ID로 거래 삭제
    # ======================================================
    # JSONL 파일은 중간 한 줄만 바로 지우기 어려우므로
    # 임시 파일을 하나 만들어 다시 작성함
    #
    # 1. 기존 거래를 한 건씩 읽음
    # 2. 삭제할 거래만 건너뜀
    # 3. 나머지는 임시 파일에 저장
    # 4. 삭제 대상이 있었다면 임시 파일로 원본을 교체
    #
    # 삭제 성공 = True
    # 없는 id   = False
    # ======================================================

    def delete_by_id(
        self,
        transaction_id: str
    ) -> bool:

        # 같은 data 폴더에 임시 파일 준비
        temp_path = self.file_path.with_suffix(
            ".tmp"
        )

        found = False

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as temp_file:

            for transaction in self.iter_transactions():

                # 삭제할 거래를 발견하면
                # 임시 파일에 쓰지 않고 건너뜀
                if transaction.id == transaction_id:

                    found = True
                    continue

                # 삭제 대상이 아닌 거래는 다시 저장
                json.dump(
                    asdict(transaction),
                    temp_file,
                    ensure_ascii=False
                )

                temp_file.write("\n")

        # 삭제할 거래가 실제로 있었다면
        # 완성된 임시 파일로 기존 파일 교체
        if found:

            temp_path.replace(
                self.file_path
            )

            return True

        # 없는 id였다면 원본은 그대로 두고
        # 필요 없는 임시 파일만 제거
        temp_path.unlink(
            missing_ok=True
        )

        return False


# ==========================================================
# [6] 카테고리 저장소 클래스
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
    # [6-1] 카테고리 저장소 초기화
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
    # [7] 기본 카테고리 자동 생성
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
    # [8] 카테고리 한 건씩 읽기
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
    # [9] 카테고리 존재 여부 확인
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
    # [10] 새 카테고리 추가
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
    # [11] 카테고리 삭제
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