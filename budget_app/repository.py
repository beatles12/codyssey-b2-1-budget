import json
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path
from typing import TextIO

from budget_app.models import Transaction


# 한 항목을 JSONL 한 줄로 저장한다.
def _write_json_line(file: TextIO, value: dict) -> None:
    json.dump(value, file, ensure_ascii=False)
    file.write('\n')

class TransactionRepository:

    # 저장 파일 경로를 준비한다.
    def __init__(self, file_path: str='data/transactions.jsonl') -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # 새 항목을 JSONL 파일에 추가한다.
    def add(self, transaction: Transaction) -> None:
        with self.file_path.open('a', encoding='utf-8') as file:
            _write_json_line(file, asdict(transaction))

    # 거래를 파일에서 한 건씩 읽는다.
    def iter_transactions(self) -> Iterator[Transaction]:
        if not self.file_path.exists():
            return
        with self.file_path.open('r', encoding='utf-8') as file:
            for line in file:
                if not line.strip():
                    continue
                data = json.loads(line)
                yield Transaction(
                    id=data['id'], type=data['type'], date=data['date'], amount=data['amount'],
                    category=data['category'], memo=data.get('memo', ''), tags=data.get('tags', []),
                )

    # ID와 일치하는 거래를 찾는다.
    def find_by_id(self, transaction_id: str) -> Transaction | None:
        for transaction in self.iter_transactions():
            if transaction.id == transaction_id:
                return transaction
        return None

    # 거래 파일을 다시 써서 지정한 거래를 수정한다.
    def update_by_id(self, transaction_id: str, updated_transaction: Transaction) -> bool:
        temp_path = self.file_path.with_suffix('.tmp')
        found = False
        with temp_path.open('w', encoding='utf-8') as temp_file:
            for transaction in self.iter_transactions():
                if transaction.id == transaction_id:
                    _write_json_line(temp_file, asdict(updated_transaction))
                    found = True
                    continue
                _write_json_line(temp_file, asdict(transaction))
        if found:
            temp_path.replace(self.file_path)
            return True
        temp_path.unlink(missing_ok=True)
        return False

    # 거래 파일을 다시 써서 지정한 거래를 삭제한다.
    def delete_by_id(self, transaction_id: str) -> bool:
        temp_path = self.file_path.with_suffix('.tmp')
        found = False
        with temp_path.open('w', encoding='utf-8') as temp_file:
            for transaction in self.iter_transactions():
                if transaction.id == transaction_id:
                    found = True
                    continue
                _write_json_line(temp_file, asdict(transaction))
        if found:
            temp_path.replace(self.file_path)
            return True
        temp_path.unlink(missing_ok=True)
        return False

class CategoryRepository:
    DEFAULT_CATEGORIES = ['food', 'coffee', 'transport', 'shopping', 'housing', 'health', 'education', 'salary', 'etc']

    # 저장 파일 경로를 준비한다.
    def __init__(self, file_path: str='data/categories.jsonl') -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            self._create_default_categories()

    # 처음 사용할 기본 카테고리를 저장한다.
    def _create_default_categories(self) -> None:
        with self.file_path.open('w', encoding='utf-8') as file:
            for category in self.DEFAULT_CATEGORIES:
                _write_json_line(file, {'name': category})

    # 카테고리를 파일에서 한 건씩 읽는다.
    def iter_categories(self) -> Iterator[str]:
        if not self.file_path.exists():
            return
        with self.file_path.open('r', encoding='utf-8') as file:
            for line in file:
                if not line.strip():
                    continue
                data = json.loads(line)
                yield data['name']

    # 카테고리의 등록 여부를 확인한다.
    def exists(self, category_name: str) -> bool:
        for category in self.iter_categories():
            if category == category_name:
                return True
        return False

    # 새 항목을 JSONL 파일에 추가한다.
    def add(self, category_name: str) -> None:
        with self.file_path.open('a', encoding='utf-8') as file:
            _write_json_line(file, {'name': category_name})

    # 지정한 카테고리를 파일에서 제거한다.
    def remove(self, category_name: str) -> bool:
        categories = list(self.iter_categories())
        if category_name not in categories:
            return False
        remaining_categories = [category for category in categories if category != category_name]
        with self.file_path.open('w', encoding='utf-8') as file:
            for category in remaining_categories:
                _write_json_line(file, {'name': category})
        return True

class BudgetRepository:

    # 저장 파일 경로를 준비한다.
    def __init__(self, file_path: str='data/budgets.jsonl') -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # 예산을 파일에서 한 건씩 읽는다.
    def iter_budgets(self) -> Iterator[dict]:
        if not self.file_path.exists():
            return
        with self.file_path.open('r', encoding='utf-8') as file:
            for line in file:
                if not line.strip():
                    continue
                yield json.loads(line)

    # 해당 월의 예산을 찾는다.
    def get_budget(self, month: str) -> int | None:
        for budget in self.iter_budgets():
            if budget['month'] == month:
                return budget['amount']
        return None

    # 해당 월의 예산을 저장하거나 덮어쓴다.
    def set_budget(self, month: str, amount: int) -> None:
        temp_path = self.file_path.with_suffix('.tmp')
        found = False
        with temp_path.open('w', encoding='utf-8') as temp_file:
            for budget in self.iter_budgets():
                if budget['month'] == month:
                    _write_json_line(temp_file, {'month': month, 'amount': amount})
                    found = True
                    continue
                _write_json_line(temp_file, budget)
            if not found:
                _write_json_line(temp_file, {'month': month, 'amount': amount})
        temp_path.replace(self.file_path)
