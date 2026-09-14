from collections import deque
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
# - 거래 추가, 조회, 검색, 수정, 삭제 업무를 처리함
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
    # --from / --to에 날짜가 들어온 경우
    # YYYY-MM-DD 형식인지 검사함
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
    # [4] 새 거래 추가
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
    # [5] 최신 거래 목록 조회
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
    # [6] 조건으로 거래 검색
    # ======================================================
    # 지원 조건:
    # - date_from        시작 날짜
    # - date_to          끝 날짜
    # - category         카테고리
    # - transaction_type 수입/지출
    # - query            메모 검색어
    # - tag              태그
    #
    # Repository의 Generator로 거래를 한 건씩 읽으면서
    # 조건에 맞지 않는 거래는 continue로 건너뜀
    #
    # 검색된 거래만 임시로 보관한 뒤
    # pop()을 이용해 최신 거래부터 yield 함
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

        # ------------------------------
        # 검색 조건 검증
        # ------------------------------

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


        # ------------------------------
        # 조건에 맞는 거래 찾기
        # ------------------------------

        matches = deque()

        for transaction in (
            self.repository.iter_transactions()
        ):

            # 시작 날짜보다 이전이면 제외
            if (
                date_from
                and transaction.date < date_from
            ):
                continue

            # 끝 날짜보다 이후이면 제외
            if (
                date_to
                and transaction.date > date_to
            ):
                continue

            # 카테고리가 다르면 제외
            if (
                category
                and transaction.category != category
            ):
                continue

            # 수입/지출 종류가 다르면 제외
            if (
                transaction_type
                and transaction.type != transaction_type
            ):
                continue

            # 메모에 검색어가 없으면 제외
            if (
                query
                and query.lower()
                not in transaction.memo.lower()
            ):
                continue

            # 태그가 없으면 제외
            if (
                tag
                and tag not in transaction.tags
            ):
                continue

            # 모든 조건을 통과한 거래만 저장
            matches.append(
                transaction
            )


        # ------------------------------
        # 최신 거래부터 하나씩 반환
        # ------------------------------

        while matches:

            yield matches.pop()


    # ======================================================
    # [7] 거래 수정
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
    # [8] 거래 삭제
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
# [9] 카테고리 서비스 클래스
# ==========================================================

class CategoryService:

    # ======================================================
    # [9-1] 카테고리 서비스 초기화
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
    # [10] 카테고리 목록 조회
    # ======================================================

    def list_categories(
        self
    ) -> list[str]:

        return list(
            self.category_repository.iter_categories()
        )


    # ======================================================
    # [11] 새 카테고리 추가
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
    # [12] 카테고리 삭제
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