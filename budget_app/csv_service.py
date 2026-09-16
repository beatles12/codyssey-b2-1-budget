import csv
from pathlib import Path

from budget_app.repository import CategoryRepository, TransactionRepository
from budget_app.service import TransactionService, _is_valid_date, _is_valid_month

CSV_FIELDNAMES = ['date', 'type', 'category', 'amount', 'memo', 'tags']


class CsvService:
    # CSV 처리에 필요한 저장소와 거래 서비스를 연결한다.
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.category_repository    = category_repository
        self.transaction_service    = TransactionService(transaction_repository)

    # 월 입력 형식을 검사한다.
    def _validate_month(self, month: str) -> None:
        if not _is_valid_month(month):
            raise ValueError('월 형식이 올바르지 않습니다. YYYY-MM 형식으로 입력해주세요.')

    # 날짜 입력 형식을 검사한다.
    def _validate_date(self, date: str) -> None:
        if not _is_valid_date(date):
            raise ValueError('날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.')

    # 조건에 맞는 거래를 CSV로 내보낸다.
    def export_transactions(
        self,
        out_path: str,
        month: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> int:
        if month:
            self._validate_month(month)
            if date_from or date_to:
                raise ValueError('--month와 --from/--to는 동시에 사용할 수 없습니다.')
        else:
            if not date_from or not date_to:
                raise ValueError('--month 또는 --from과 --to를 입력해야 합니다.')

            self._validate_date(date_from)
            self._validate_date(date_to)

            if date_from > date_to:
                raise ValueError('시작 날짜는 끝 날짜보다 늦을 수 없습니다.')

        output_file   = Path(out_path)
        exported_count = 0

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open('w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for transaction in self.transaction_repository.iter_transactions():
                if month and not transaction.date.startswith(month):
                    continue
                if date_from and transaction.date < date_from:
                    continue
                if date_to and transaction.date > date_to:
                    continue

                writer.writerow({
                    'date': transaction.date,
                    'type': transaction.type,
                    'category': transaction.category,
                    'amount': transaction.amount,
                    'memo': transaction.memo,
                    'tags': ','.join(transaction.tags),
                })
                exported_count += 1

        return exported_count

    # CSV 한 행의 필수값을 읽고 검사한다.
    def _prepare_import_row(self, row: dict[str, str | None]) -> dict | None:
        date             = (row.get('date') or '').strip()
        transaction_type = (row.get('type') or '').strip()
        category         = (row.get('category') or '').strip()
        amount_text      = (row.get('amount') or '').strip()
        memo             = (row.get('memo') or '').strip()
        tags_text        = (row.get('tags') or '').strip()

        if not amount_text.isdigit():
            return None

        amount = int(amount_text)

        error = self.transaction_service.get_transaction_validation_error(
            transaction_type, date, amount, category
        )
        if error:
            return None

        if not self.category_repository.exists(category):
            return None

        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []

        return {
            'transaction_type': transaction_type,
            'date': date,
            'amount': amount,
            'category': category,
            'memo': memo,
            'tags': tags,
        }

    # CSV를 행 단위로 검증해 거래를 가져온다.
    def import_transactions(self, from_path: str) -> tuple[int, int]:
        input_file = Path(from_path)
        if not input_file.exists():
            raise ValueError(f'CSV 파일을 찾을 수 없습니다: {from_path}')

        imported_count = 0
        skipped_count  = 0

        with input_file.open('r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError('CSV 헤더가 없습니다.')

            missing_columns = [
                field for field in CSV_FIELDNAMES
                if field not in reader.fieldnames
            ]
            if missing_columns:
                raise ValueError('CSV 필수 열이 없습니다: ' + ', '.join(missing_columns))

            for row in reader:
                prepared_row = self._prepare_import_row(row)

                if prepared_row is None:
                    skipped_count += 1
                    continue

                self.transaction_service.add_transaction(**prepared_row)
                imported_count += 1

        return imported_count, skipped_count