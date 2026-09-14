from collections import defaultdict, deque
from collections.abc import Iterator
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
# - 거래 추가, 조회, 검색, 요약, 수정, 삭제 업무를 처리함
# - 잘못된 입력값을 검사함
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
    # [3] 검색 날짜 형식 검증
    # ======================================================

    def _validate_search_date(
        self,
        date: str
    ) -> None:

        try:
            datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError as error:
            raise ValueError(
                "검색 날짜는 YYYY-MM-DD 형식이어야 합니다."
            ) from error


    # ======================================================
    # [4] 월 형식 검증
    # ======================================================
    # summary에서 사용하는 YYYY-MM 형식을 검사함
    #
    # 예:
    # 2026-09  → 정상
    # 2026-13  → 오류
    # ======================================================

    def _validate_month(
        self,
        month: str
    ) -> None:

        try:
            datetime.strptime(
                month,
                "%Y-%m"
            )

        except ValueError as error:
            raise ValueError(
                "월은 YYYY-MM 형식으로 입력해야 합니다."
            ) from error


    # ======================================================
    # [5] 새 거래 추가
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
    # [6] 최신 거래 목록 조회
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
    # [7] 조건으로 거래 검색
    # ======================================================

    def search_transactions(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
        query: str | None = None,
        tag: str | None = None,
    ) -> Iterator[Transaction]:

        if date_from:
            self._validate_search_date(
                date_from
            )

        if date_to:
            self._validate_search_date(
                date_to
            )

        if (
            date_from
            and date_to
            and date_from > date_to
        ):
            raise ValueError(
                "시작 날짜는 끝 날짜보다 늦을 수 없습니다."
            )

        if (
            transaction_type
            and transaction_type not in (
                "income",
                "expense"
            )
        ):
            raise ValueError(
                "검색 타입은 income 또는 expense만 가능합니다."
            )

        matches = deque()

        for transaction in (
            self.repository.iter_transactions()
        ):

            if (
                date_from
                and transaction.date < date_from
            ):
                continue

            if (
                date_to
                and transaction.date > date_to
            ):
                continue

            if (
                category
                and transaction.category != category
            ):
                continue

            if (
                transaction_type
                and transaction.type != transaction_type
            ):
                continue

            if (
                query
                and query.lower()
                not in transaction.memo.lower()
            ):
                continue

            if (
                tag
                and tag not in transaction.tags
            ):
                continue

            matches.append(
                transaction
            )

        while matches:
            yield matches.pop()


    # ======================================================
    # [8] 월별 요약 계산
    # ======================================================
    # 해당 월의 거래를 한 건씩 읽으면서
    # 총수입, 총지출, 잔액을 계산함
    #
    # expense 거래는 카테고리별로 합산하고
    # 금액이 큰 순서대로 TOP N을 만듦
    # ======================================================

    def summarize_month(
        self,
        month: str,
        top: int = 3,
    ) -> dict:

        # YYYY-MM 형식 검사
        self._validate_month(
            month
        )

        if top <= 0:
            raise ValueError(
                "TOP 개수는 1 이상이어야 합니다."
            )

        total_income = 0
        total_expense = 0
        transaction_count = 0

        # 카테고리별 지출 금액 저장
        category_expenses = defaultdict(int)

        # 파일을 한 건씩 읽으면서 계산
        for transaction in (
            self.repository.iter_transactions()
        ):

            # 해당 월이 아니면 건너뜀
            if not transaction.date.startswith(
                month
            ):
                continue

            transaction_count += 1

            # 수입 합계
            if transaction.type == "income":

                total_income += (
                    transaction.amount
                )

            # 지출 합계 + 카테고리별 합계
            elif transaction.type == "expense":

                total_expense += (
                    transaction.amount
                )

                category_expenses[
                    transaction.category
                ] += transaction.amount


        # 수입 - 지출 = 잔액
        balance = (
            total_income
            - total_expense
        )


        # 카테고리별 지출을 큰 금액 순으로 정렬
        top_categories = sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:top]


        # 계산 결과를 하나의 딕셔너리로 반환
        return {
            "month": month,
            "transaction_count": transaction_count,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "top_categories": top_categories,
        }


    # ======================================================
    # [9] 거래 수정
    # ======================================================

    def update_transaction(
        self,
        transaction_id: str,
        transaction_type: str | None = None,
        date: str | None = None,
        amount: int | None = None,
        category: str | None = None,
        memo: str | None = None,
        tags: list[str] | None = None,
    ) -> Transaction:

        transaction_id = (
            transaction_id.strip()
        )

        if not transaction_id:
            raise ValueError(
                "거래 id를 입력해야 합니다."
            )

        current = self.repository.find_by_id(
            transaction_id
        )

        if current is None:
            raise ValueError(
                "해당 id의 거래를 찾을 수 없습니다."
            )

        new_type = (
            transaction_type
            if transaction_type is not None
            else current.type
        )

        new_date = (
            date
            if date is not None
            else current.date
        )

        new_amount = (
            amount
            if amount is not None
            else current.amount
        )

        new_category = (
            category
            if category is not None
            else current.category
        )

        new_memo = (
            memo
            if memo is not None
            else current.memo
        )

        new_tags = (
            tags
            if tags is not None
            else current.tags
        )

        self._validate_transaction_input(
            new_type,
            new_date,
            new_amount,
            new_category,
        )

        updated_transaction = Transaction(
            id=current.id,
            type=new_type,
            date=new_date,
            amount=new_amount,
            category=new_category,
            memo=new_memo,
            tags=new_tags,
        )

        updated = self.repository.update_by_id(
            transaction_id,
            updated_transaction,
        )

        if not updated:
            raise ValueError(
                "거래 수정에 실패했습니다."
            )

        return updated_transaction


    # ======================================================
    # [10] 거래 삭제
    # ======================================================

    def delete_transaction(
        self,
        transaction_id: str
    ) -> None:

        transaction_id = (
            transaction_id.strip()
        )

        if not transaction_id:
            raise ValueError(
                "거래 id를 입력해야 합니다."
            )

        transaction = self.repository.find_by_id(
            transaction_id
        )

        if transaction is None:
            raise ValueError(
                "해당 id의 거래를 찾을 수 없습니다."
            )

        deleted = self.repository.delete_by_id(
            transaction_id
        )

        if not deleted:
            raise ValueError(
                "거래 삭제에 실패했습니다."
            )


# ==========================================================
# [11] 카테고리 서비스 클래스
# ==========================================================

class CategoryService:

    # ======================================================
    # [11-1] 카테고리 서비스 초기화
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
    # [12] 카테고리 목록 조회
    # ======================================================

    def list_categories(
        self
    ) -> list[str]:

        return list(
            self.category_repository.iter_categories()
        )


    # ======================================================
    # [13] 새 카테고리 추가
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
    # [14] 카테고리 삭제
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