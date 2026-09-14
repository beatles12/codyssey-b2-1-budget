from collections import deque
from datetime import datetime
from uuid import uuid4

from budget_app.models import Transaction
from budget_app.repository import (
    CategoryRepository,
    TransactionRepository,
)


# ==========================================================
# [1] 거래 서비스 클래스
# ==========================================================
# 역할:
# - 거래 추가, 조회, 삭제 등 거래 업무 규칙을 처리함
# - 잘못된 입력을 검사함
# - 실제 파일 작업은 Repository에 맡김
# ==========================================================

class TransactionService:

    # ======================================================
    # [1-1] 거래 서비스 초기화
    # ======================================================

    def __init__(
        self,
        repository: TransactionRepository
    ) -> None:

        self.repository = repository


    # ======================================================
    # [2] 거래 입력값 검증
    # ======================================================

    def _validate_transaction_input(
        self,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
    ) -> None:

        if transaction_type not in (
            "income",
            "expense"
        ):
            raise ValueError(
                "거래 종류는 income 또는 expense만 가능합니다."
            )

        try:
            datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError as error:
            raise ValueError(
                "날짜는 YYYY-MM-DD 형식으로 입력해야 합니다."
            ) from error

        if amount <= 0:
            raise ValueError(
                "금액은 0보다 큰 양수여야 합니다."
            )

        if not category.strip():
            raise ValueError(
                "카테고리는 비워둘 수 없습니다."
            )


    # ======================================================
    # [3] 새 거래 추가
    # ======================================================

    def add_transaction(
        self,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
        memo: str = "",
        tags: list[str] | None = None,
    ) -> Transaction:

        self._validate_transaction_input(
            transaction_type,
            date,
            amount,
            category,
        )

        transaction_id = str(
            uuid4()
        )

        if tags is None:
            tags = []

        transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags,
        )

        self.repository.add(
            transaction
        )

        return transaction


    # ======================================================
    # [4] 최신 거래 목록 조회
    # ======================================================
    # Generator로 거래를 한 건씩 읽고
    # deque를 이용해 마지막 N건만 보관함
    # ======================================================

    def list_transactions(
        self,
        limit: int = 20
    ) -> list[Transaction]:

        if limit <= 0:
            raise ValueError(
                "조회 개수는 1 이상이어야 합니다."
            )

        recent_transactions = deque(
            maxlen=limit
        )

        for transaction in (
            self.repository.iter_transactions()
        ):
            recent_transactions.append(
                transaction
            )

        return list(
            reversed(
                recent_transactions
            )
        )


    # ======================================================
    # [5] 거래 삭제
    # ======================================================
    # 사용자가 입력한 id가 실제로 존재하는지 먼저 확인함
    #
    # 존재함:
    # - Repository에 삭제 요청
    #
    # 존재하지 않음:
    # - ValueError를 발생시켜
    #   나중에 CLI에서 이해하기 쉬운 메시지로 보여줌
    # ======================================================

    def delete_transaction(
        self,
        transaction_id: str
    ) -> None:

        transaction_id = (
            transaction_id.strip()
        )

        # 빈 id는 허용하지 않음
        if not transaction_id:
            raise ValueError(
                "거래 id를 입력해야 합니다."
            )

        # 해당 id의 거래가 실제로 존재하는지 확인
        transaction = self.repository.find_by_id(
            transaction_id
        )

        if transaction is None:
            raise ValueError(
                "해당 id의 거래를 찾을 수 없습니다."
            )

        # 존재하는 거래이면 Repository에 삭제 요청
        deleted = self.repository.delete_by_id(
            transaction_id
        )

        if not deleted:
            raise ValueError(
                "거래 삭제에 실패했습니다."
            )


# ==========================================================
# [6] 카테고리 서비스 클래스
# ==========================================================
# 역할:
# - 카테고리 추가 / 조회 / 삭제 업무를 처리함
# - 중복 카테고리를 막음
# - 실제 거래에서 사용 중인 카테고리는 삭제하지 못하게 함
# ==========================================================

class CategoryService:

    # ======================================================
    # [6-1] 카테고리 서비스 초기화
    # ======================================================

    def __init__(
        self,
        category_repository: CategoryRepository,
        transaction_repository: TransactionRepository,
    ) -> None:

        self.category_repository = (
            category_repository
        )

        self.transaction_repository = (
            transaction_repository
        )


    # ======================================================
    # [7] 카테고리 목록 조회
    # ======================================================

    def list_categories(
        self
    ) -> list[str]:

        return list(
            self.category_repository.iter_categories()
        )


    # ======================================================
    # [8] 새 카테고리 추가
    # ======================================================

    def add_category(
        self,
        category_name: str
    ) -> None:

        category_name = (
            category_name.strip()
        )

        if not category_name:
            raise ValueError(
                "카테고리 이름은 비워둘 수 없습니다."
            )

        if self.category_repository.exists(
            category_name
        ):
            raise ValueError(
                "이미 존재하는 카테고리입니다."
            )

        self.category_repository.add(
            category_name
        )


    # ======================================================
    # [9] 카테고리 삭제
    # ======================================================

    def remove_category(
        self,
        category_name: str
    ) -> None:

        category_name = (
            category_name.strip()
        )

        if not self.category_repository.exists(
            category_name
        ):
            raise ValueError(
                "존재하지 않는 카테고리입니다."
            )

        for transaction in (
            self.transaction_repository.iter_transactions()
        ):

            if (
                transaction.category
                == category_name
            ):
                raise ValueError(
                    "사용 중인 카테고리는 삭제할 수 없습니다."
                )

        self.category_repository.remove(
            category_name
        )