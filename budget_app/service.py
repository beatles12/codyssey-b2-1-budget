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
# - 거래 추가, 검증, 목록 조회 등
#   거래와 관련된 업무 규칙을 처리함
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


# ==========================================================
# [5] 카테고리 서비스 클래스
# ==========================================================
# 역할:
# - 카테고리 추가 / 조회 / 삭제 업무를 처리함
# - 중복 카테고리를 막음
# - 실제 거래에서 사용 중인 카테고리는 삭제하지 못하게 함
# ==========================================================

class CategoryService:

    # ======================================================
    # [5-1] 카테고리 서비스 초기화
    # ======================================================
    # 카테고리 저장소와 거래 저장소를 둘 다 전달받음
    #
    # 카테고리 저장소:
    # - 카테고리 추가/삭제/조회
    #
    # 거래 저장소:
    # - 삭제하려는 카테고리가 실제 거래에서
    #   사용 중인지 확인할 때 필요함
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
    # [6] 카테고리 목록 조회
    # ======================================================

    def list_categories(
        self
    ) -> list[str]:

        return list(
            self.category_repository.iter_categories()
        )


    # ======================================================
    # [7] 새 카테고리 추가
    # ======================================================
    # 빈 이름은 허용하지 않음
    # 이미 같은 이름이 존재하면 중복 추가를 막음
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
    # [8] 카테고리 삭제
    # ======================================================
    # 1. 카테고리가 존재하는지 확인
    # 2. 거래에서 사용 중인지 확인
    # 3. 사용 중이면 삭제 금지
    # 4. 사용되지 않는 경우에만 삭제
    # ======================================================

    def remove_category(
        self,
        category_name: str
    ) -> None:

        category_name = (
            category_name.strip()
        )

        # 카테고리 자체가 없는 경우
        if not self.category_repository.exists(
            category_name
        ):
            raise ValueError(
                "존재하지 않는 카테고리입니다."
            )

        # 실제 거래에서 사용 중인지 확인
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

        # 아무 거래에서도 사용되지 않았다면 삭제
        self.category_repository.remove(
            category_name
        )