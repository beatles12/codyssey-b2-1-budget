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
# - 거래 수정과 삭제도 담당함
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
    # [3] 거래 한 건씩 읽기
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
    # [4] ID로 거래 찾기
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

                if transaction.id == transaction_id:

                    json.dump(
                        asdict(updated_transaction),
                        temp_file,
                        ensure_ascii=False
                    )

                    temp_file.write("\n")

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


    # ======================================================
    # [6] ID로 거래 삭제
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
    # [8] 기본 카테고리 생성
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


# ==========================================================
# [13] 예산 저장소 클래스
# ==========================================================
# 역할:
# - 월별 예산을 JSONL 파일에 영구 저장함
# - 기본 저장 파일은 data/budgets.jsonl
#
# 예:
# {"month": "2026-09", "amount": 500000}
# ==========================================================

class BudgetRepository:

    # ======================================================
    # [13-1] 예산 저장소 초기화
    # ======================================================

    def __init__(
        self,
        file_path: str = "data/budgets.jsonl"
    ) -> None:

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    # ======================================================
    # [14] 저장된 예산 한 건씩 읽기
    # ======================================================

    def iter_budgets(
        self
    ) -> Iterator[dict]:

        if not self.file_path.exists():
            return

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                yield json.loads(
                    line
                )


    # ======================================================
    # [15] 특정 월의 예산 조회
    # ======================================================
    # 해당 월의 예산이 있으면 금액을 반환함
    # 없으면 None 반환
    # ======================================================

    def get_budget(
        self,
        month: str
    ) -> int | None:

        for budget in self.iter_budgets():

            if budget["month"] == month:

                return budget["amount"]

        return None


    # ======================================================
    # [16] 월별 예산 저장 또는 수정
    # ======================================================
    # 같은 월의 예산이 이미 있으면 금액을 수정함
    # 없는 월이면 새 예산을 추가함
    #
    # 예:
    # 2026-09 = 500000 저장
    #
    # 다시
    # 2026-09 = 600000 저장
    #
    # → 두 줄이 생기는 것이 아니라
    #   기존 2026-09 예산을 600000으로 교체함
    # ======================================================

    def set_budget(
        self,
        month: str,
        amount: int,
    ) -> None:

        temp_path = self.file_path.with_suffix(
            ".tmp"
        )

        found = False

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as temp_file:

            for budget in self.iter_budgets():

                # 같은 월을 발견하면 새 금액으로 교체
                if budget["month"] == month:

                    json.dump(
                        {
                            "month": month,
                            "amount": amount,
                        },
                        temp_file,
                        ensure_ascii=False
                    )

                    temp_file.write("\n")

                    found = True
                    continue

                # 다른 월의 예산은 그대로 저장
                json.dump(
                    budget,
                    temp_file,
                    ensure_ascii=False
                )

                temp_file.write("\n")


            # 같은 월의 예산이 없었다면 새로 추가
            if not found:

                json.dump(
                    {
                        "month": month,
                        "amount": amount,
                    },
                    temp_file,
                    ensure_ascii=False
                )

                temp_file.write("\n")


        # 완성된 임시 파일을 budgets.jsonl로 교체
        temp_path.replace(
            self.file_path
        )