from calendar import monthrange
from collections import defaultdict, deque
from collections.abc import Iterator
from uuid import uuid4

from budget_app.models import Transaction
from budget_app.repository import BudgetRepository, CategoryRepository, TransactionRepository


# YYYY-MM-DD 형식의 실제 날짜인지 확인한다.
def _is_valid_date(date: str) -> bool:
    parts = date.split('-')
    if len(parts) != 3:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False
    if not all(part.isdigit() for part in parts):
        return False

    year, month, day = map(int, parts)
    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        return False

    return 1 <= day <= monthrange(year, month)[1]


# YYYY-MM 형식의 실제 월인지 확인한다.
def _is_valid_month(month: str) -> bool:
    parts = month.split('-')
    if len(parts) != 2:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2:
        return False
    if not all(part.isdigit() for part in parts):
        return False

    year, month_number = map(int, parts)
    return 1 <= year <= 9999 and 1 <= month_number <= 12


class TransactionService:
    # 서비스에 필요한 저장소를 연결한다.
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    # 거래 입력값의 오류 메시지를 돌려준다.
    def get_transaction_validation_error(
        self, transaction_type: str, date: str, amount: int, category: str
    ) -> str | None:
        if transaction_type not in ('income', 'expense'):
            return '거래 종류는 income 또는 expense만 가능합니다.'
        if not _is_valid_date(date):
            return '날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.'
        if amount <= 0:
            return '금액은 0보다 큰 양수여야 합니다.'
        if not category.strip():
            return '카테고리는 비워둘 수 없습니다.'
        return None

    # 검색 날짜 형식을 검사한다.
    def _validate_search_date(self, date: str) -> None:
        if not _is_valid_date(date):
            raise ValueError('날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.')

    # 월 입력 형식을 검사한다.
    def _validate_month(self, month: str) -> None:
        if not _is_valid_month(month):
            raise ValueError('월 형식이 올바르지 않습니다. YYYY-MM 형식으로 입력해주세요.')

    # 검증한 거래에 ID를 붙여 저장한다.
    def add_transaction(
        self,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
        memo: str = '',
        tags: list[str] | None = None,
    ) -> Transaction:
        error = self.get_transaction_validation_error(transaction_type, date, amount, category)
        if error:
            raise ValueError(error)

        transaction_id = str(uuid4())
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
        self.repository.add(transaction)
        return transaction

    # 최근 거래를 지정한 수만큼 돌려준다.
    def list_transactions(self, limit: int = 20) -> list[Transaction]:
        if limit <= 0:
            raise ValueError('조회 개수는 1 이상이어야 합니다.')

        recent_transactions = deque(maxlen=limit)
        for transaction in self.repository.iter_transactions():
            recent_transactions.append(transaction)

        return list(reversed(recent_transactions))

    # 조건에 맞는 거래를 최신순으로 돌려준다.
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
            self._validate_search_date(date_from)
        if date_to:
            self._validate_search_date(date_to)
        if date_from and date_to and date_from > date_to:
            raise ValueError('시작 날짜는 끝 날짜보다 늦을 수 없습니다.')
        if transaction_type and transaction_type not in ('income', 'expense'):
            raise ValueError('검색 타입은 income 또는 expense만 가능합니다.')

        matches = deque()
        for transaction in self.repository.iter_transactions():
            if date_from and transaction.date < date_from:
                continue
            if date_to and transaction.date > date_to:
                continue
            if category and transaction.category != category:
                continue
            if transaction_type and transaction.type != transaction_type:
                continue
            if query and query.lower() not in transaction.memo.lower():
                continue
            if tag and tag not in transaction.tags:
                continue
            matches.append(transaction)

        while matches:
            yield matches.pop()

    # 월별 수입과 지출 및 상위 카테고리를 계산한다.
    def summarize_month(self, month: str, top: int = 3) -> dict:
        self._validate_month(month)
        if top <= 0:
            raise ValueError('TOP 개수는 1 이상이어야 합니다.')

        total_income      = 0
        total_expense     = 0
        transaction_count = 0
        category_expenses = defaultdict(int)

        for transaction in self.repository.iter_transactions():
            if not transaction.date.startswith(month):
                continue

            transaction_count += 1

            if transaction.type == 'income':
                total_income += transaction.amount
            elif transaction.type == 'expense':
                total_expense += transaction.amount
                category_expenses[transaction.category] += transaction.amount

        balance        = total_income - total_expense
        top_categories = sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:top]

        return {
            'month': month,
            'transaction_count': transaction_count,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'top_categories': top_categories,
        }

    # 변경값을 검증하고 거래를 수정한다.
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
        transaction_id = transaction_id.strip()
        if not transaction_id:
            raise ValueError('거래 id를 입력해야 합니다.')

        current = self.repository.find_by_id(transaction_id)
        if current is None:
            raise ValueError('해당 id의 거래를 찾을 수 없습니다.')

        new_type     = transaction_type if transaction_type is not None else current.type
        new_date     = date if date is not None else current.date
        new_amount   = amount if amount is not None else current.amount
        new_category = category if category is not None else current.category
        new_memo     = memo if memo is not None else current.memo
        new_tags     = tags if tags is not None else current.tags

        error = self.get_transaction_validation_error(
            new_type, new_date, new_amount, new_category
        )
        if error:
            raise ValueError(error)

        updated_transaction = Transaction(
            id=current.id,
            type=new_type,
            date=new_date,
            amount=new_amount,
            category=new_category,
            memo=new_memo,
            tags=new_tags,
        )

        updated = self.repository.update_by_id(transaction_id, updated_transaction)
        if not updated:
            raise ValueError('거래 수정에 실패했습니다.')

        return updated_transaction

    # ID를 확인하고 거래를 삭제한다.
    def delete_transaction(self, transaction_id: str) -> None:
        transaction_id = transaction_id.strip()
        if not transaction_id:
            raise ValueError('거래 id를 입력해야 합니다.')

        transaction = self.repository.find_by_id(transaction_id)
        if transaction is None:
            raise ValueError('해당 id의 거래를 찾을 수 없습니다.')

        deleted = self.repository.delete_by_id(transaction_id)
        if not deleted:
            raise ValueError('거래 삭제에 실패했습니다.')


class CategoryService:
    # 서비스에 필요한 저장소를 연결한다.
    def __init__(
        self,
        category_repository: CategoryRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self.category_repository    = category_repository
        self.transaction_repository = transaction_repository

    # 등록된 카테고리 목록을 돌려준다.
    def list_categories(self) -> list[str]:
        return list(self.category_repository.iter_categories())

    # 중복 여부를 확인하고 카테고리를 추가한다.
    def add_category(self, category_name: str) -> None:
        category_name = category_name.strip()
        if not category_name:
            raise ValueError('카테고리 이름은 비워둘 수 없습니다.')
        if self.category_repository.exists(category_name):
            raise ValueError('이미 존재하는 카테고리입니다.')

        self.category_repository.add(category_name)

    # 사용 중인지 확인하고 카테고리를 삭제한다.
    def remove_category(self, category_name: str) -> None:
        category_name = category_name.strip()
        if not self.category_repository.exists(category_name):
            raise ValueError('존재하지 않는 카테고리입니다.')

        for transaction in self.transaction_repository.iter_transactions():
            if transaction.category == category_name:
                raise ValueError('사용 중인 카테고리는 삭제할 수 없습니다.')

        self.category_repository.remove(category_name)


class BudgetService:
    # 서비스에 필요한 저장소를 연결한다.
    def __init__(self, repository: BudgetRepository) -> None:
        self.repository = repository

    # 월과 예산 금액을 검사한다.
    def _validate_budget(self, month: str, amount: int) -> None:
        if not _is_valid_month(month):
            raise ValueError('월 형식이 올바르지 않습니다. YYYY-MM 형식으로 입력해주세요.')
        if amount <= 0:
            raise ValueError('예산은 0보다 큰 금액이어야 합니다.')

    # 검증한 월 예산을 저장한다.
    def set_budget(self, month: str, amount: int) -> None:
        self._validate_budget(month, amount)
        self.repository.set_budget(month, amount)

    # 월을 검증하고 저장된 예산을 읽는다.
    def get_budget(self, month: str) -> int | None:
        if not _is_valid_month(month):
            raise ValueError('월 형식이 올바르지 않습니다. YYYY-MM 형식으로 입력해주세요.')

        return self.repository.get_budget(month)

    # 예산 사용률과 남은 금액을 계산한다.
    def get_budget_status(self, month: str, spent: int) -> dict | None:
        budget = self.get_budget(month)
        if budget is None:
            return None

        usage_rate = spent / budget * 100
        remaining  = budget - spent
        exceeded   = spent > budget

        return {
            'budget': budget,
            'spent': spent,
            'usage_rate': usage_rate,
            'remaining': remaining,
            'exceeded': exceeded,
        }