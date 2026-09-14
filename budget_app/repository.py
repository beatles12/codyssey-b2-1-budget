import json
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path

from budget_app.models import Transaction


# ==========================================================
# [1] 거래 저장소 클래스
# ==========================================================
# 역할:
# - Transaction 데이터를 파일에 저장하고 다시 불러옴
# - 기본 저장 파일은 data/transactions.jsonl
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

    def add(self, transaction: Transaction) -> None:

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
    # yield를 사용해 파일을 한 줄씩 읽음
    # ======================================================

    def iter_transactions(self) -> Iterator[Transaction]:

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


# ==========================================================
# [4] 카테고리 저장소 클래스
# ==========================================================
# 역할:
# - 사용할 수 있는 카테고리를 파일로 관리함
# - 기본 저장 파일은 data/categories.jsonl
# - 처음 실행할 때 기본 카테고리를 자동 생성함
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
    # [4-1] 카테고리 저장소 초기화
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

        # 파일이 없거나 비어 있으면 기본 카테고리 생성
        if (
            not self.file_path.exists()
            or self.file_path.stat().st_size == 0
        ):
            self._create_default_categories()


    # ======================================================
    # [5] 기본 카테고리 자동 생성
    # ======================================================

    def _create_default_categories(self) -> None:

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
    # [6] 카테고리 한 건씩 읽기
    # ======================================================

    def iter_categories(self) -> Iterator[str]:

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
    # [7] 카테고리 존재 여부 확인
    # ======================================================
    # 같은 이름의 카테고리가 이미 있는지 검사함
    # True  = 존재함
    # False = 존재하지 않음
    # ======================================================

    def exists(self, category_name: str) -> bool:

        for category in self.iter_categories():

            if category == category_name:
                return True

        return False


    # ======================================================
    # [8] 새 카테고리 추가
    # ======================================================
    # JSONL 파일 끝에 카테고리 한 건을 추가함
    # ======================================================

    def add(self, category_name: str) -> None:

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
    # [9] 카테고리 삭제
    # ======================================================
    # 삭제할 카테고리를 제외한 나머지 카테고리를
    # 다시 파일에 저장함
    #
    # 삭제 성공  → True
    # 없는 항목  → False
    # ======================================================

    def remove(
        self,
        category_name: str
    ) -> bool:

        categories = list(
            self.iter_categories()
        )

        # 삭제할 카테고리가 없으면 False
        if category_name not in categories:
            return False

        # 삭제 대상만 제외
        remaining_categories = [
            category
            for category in categories
            if category != category_name
        ]

        # 남은 카테고리로 파일 다시 작성
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