from datetime import datetime
from uuid import uuid4

from budget_app.models import Transaction
from budget_app.repository import TransactionRepository


# ==========================================================
# [1] 거래 서비스 클래스
# ==========================================================
# 역할:
# - 사용자가 요청한 거래 관련 업무를 처리함
# - 입력값이 올바른지 검사함
# - Transaction 객체를 생성함
# - Repository에 저장을 요청함
#
# models.py      = 거래 데이터의 구조
# repository.py  = 파일 저장/읽기
# service.py     = 거래 업무 규칙과 처리 흐름
# ==========================================================

class TransactionService:

    # ======================================================
    # [1-1] 서비스 초기화
    # ======================================================
    # TransactionService 객체를 만들 때
    # 사용할 TransactionRepository를 전달받아 저장함
    # ======================================================

    def __init__(
        self,
        repository: TransactionRepository
    ) -> None:

        self.repository = repository


    # ======================================================
    # [2] 거래 입력값 검증
    # ======================================================
    # 새 거래를 저장하기 전에 잘못된 입력을 검사함
    #
    # type:
    # - income 또는 expense만 허용
    #
    # date:
    # - YYYY-MM-DD 형식인지 검사
    #
    # amount:
    # - 0보다 큰 금액만 허용
    #
    # category:
    # - 빈 문자열은 허용하지 않음
    #
    # 잘못된 값이 들어오면 ValueError를 발생시킴
    # 사용자용 오류 메시지는 이후 cli.py에서 처리할 예정
    # ======================================================

    def _validate_transaction_input(
        self,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
    ) -> None:

        # 거래 종류 검사
        if transaction_type not in ("income", "expense"):
            raise ValueError(
                "거래 종류는 income 또는 expense만 가능합니다."
            )

        # 날짜 형식 검사
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as error:
            raise ValueError(
                "날짜는 YYYY-MM-DD 형식으로 입력해야 합니다."
            ) from error

        # 금액 검사
        if amount <= 0:
            raise ValueError(
                "금액은 0보다 큰 양수여야 합니다."
            )

        # 카테고리 빈 값 검사
        if not category.strip():
            raise ValueError(
                "카테고리는 비워둘 수 없습니다."
            )


    # ======================================================
    # [3] 새 거래 추가
    # ======================================================
    # 1. 입력값 검증
    # 2. 고유 id 자동 생성
    # 3. Transaction 객체 생성
    # 4. Repository를 통해 JSONL 파일에 저장
    # 5. 저장한 Transaction 객체 반환
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

        # 저장 전에 입력값 검사
        self._validate_transaction_input(
            transaction_type,
            date,
            amount,
            category,
        )

        # 거래마다 겹치지 않는 고유 id 생성
        transaction_id = str(uuid4())

        # 태그를 입력하지 않으면 빈 리스트 사용
        if tags is None:
            tags = []

        # 입력값으로 Transaction 객체 생성
        transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags,
        )

        # Repository에 거래 저장 요청
        self.repository.add(transaction)

        # 저장한 거래 정보를 호출한 곳에 반환
        return transaction