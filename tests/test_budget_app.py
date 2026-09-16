import csv
import tempfile
import unittest
from pathlib import Path

from budget_app.csv_service import CsvService
from budget_app.repository import BudgetRepository, CategoryRepository, TransactionRepository
from budget_app.service import BudgetService, CategoryService, TransactionService

class BudgetAppTestCase(unittest.TestCase):

    # 테스트마다 별도 임시 저장소를 만든다.
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.transaction_repository = TransactionRepository(str(self.base_path / 'transactions.jsonl'))
        self.category_repository = CategoryRepository(str(self.base_path / 'categories.jsonl'))
        self.budget_repository = BudgetRepository(str(self.base_path / 'budgets.jsonl'))
        self.transaction_service = TransactionService(self.transaction_repository)
        self.category_service = CategoryService(self.category_repository, self.transaction_repository)
        self.budget_service = BudgetService(self.budget_repository)
        self.csv_service = CsvService(self.transaction_repository, self.category_repository)

    # 테스트 임시 저장소를 정리한다.
    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    # 거래 추가와 최근 목록을 확인한다.
    def test_add_and_list_transactions(self) -> None:
        created = self.transaction_service.add_transaction(
            transaction_type='expense', date='2026-09-15', amount=5000,
            category='coffee', memo='아메리카노', tags=['drink'],
        )
        transactions = self.transaction_service.list_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].id, created.id)
        self.assertEqual(transactions[0].amount, 5000)

    # 0원 거래 거부를 확인한다.
    def test_invalid_amount(self) -> None:
        with self.assertRaises(ValueError):
            self.transaction_service.add_transaction(
                transaction_type='expense', date='2026-09-15',
                amount=0, category='food',
            )

    # 카테고리 검색을 확인한다.
    def test_search_by_category(self) -> None:
        self.transaction_service.add_transaction('expense', '2026-09-15', 10000, 'food', '점심')
        self.transaction_service.add_transaction('expense', '2026-09-15', 5000, 'coffee', '커피')
        results = list(self.transaction_service.search_transactions(category='coffee'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, 'coffee')

    # 월별 수입과 지출 계산을 확인한다.
    def test_monthly_summary(self) -> None:
        self.transaction_service.add_transaction('income', '2026-09-15', 100000, 'salary')
        self.transaction_service.add_transaction('expense', '2026-09-15', 30000, 'food')
        summary = self.transaction_service.summarize_month('2026-09', 3)
        self.assertEqual(summary['total_income'], 100000)
        self.assertEqual(summary['total_expense'], 30000)
        self.assertEqual(summary['balance'], 70000)

    # 거래 수정과 파일 저장을 확인한다.
    def test_update_transaction(self) -> None:
        transaction = self.transaction_service.add_transaction('expense', '2026-09-15', 10000, 'food')
        updated = self.transaction_service.update_transaction(transaction.id, amount=15000)
        self.assertEqual(updated.amount, 15000)
        saved = self.transaction_repository.find_by_id(transaction.id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.amount, 15000)

    # 거래 삭제를 확인한다.
    def test_delete_transaction(self) -> None:
        transaction = self.transaction_service.add_transaction('expense', '2026-09-15', 10000, 'food')
        self.transaction_service.delete_transaction(transaction.id)
        result = self.transaction_repository.find_by_id(transaction.id)
        self.assertIsNone(result)

    # 카테고리 추가와 삭제를 확인한다.
    def test_category_add_and_remove(self) -> None:
        self.category_service.add_category('travel')
        self.assertTrue(self.category_repository.exists('travel'))
        self.category_service.remove_category('travel')
        self.assertFalse(self.category_repository.exists('travel'))

    # 사용 중인 카테고리 삭제 방지를 확인한다.
    def test_category_in_use_cannot_be_removed(self) -> None:
        self.transaction_service.add_transaction('expense', '2026-09-15', 10000, 'food')
        with self.assertRaises(ValueError):
            self.category_service.remove_category('food')

    # 예산 저장과 조회를 확인한다.
    def test_budget_set_and_get(self) -> None:
        self.budget_service.set_budget('2026-09', 600000)
        budget = self.budget_service.get_budget('2026-09')
        self.assertEqual(budget, 600000)

    # 예산 사용률을 확인한다.
    def test_budget_status(self) -> None:
        self.budget_service.set_budget('2026-09', 100000)
        status = self.budget_service.get_budget_status('2026-09', 40000)
        self.assertIsNotNone(status)
        self.assertEqual(status['remaining'], 60000)
        self.assertFalse(status['exceeded'])
        self.assertAlmostEqual(status['usage_rate'], 40.0)

    # CSV 내보내기 결과를 확인한다.
    def test_csv_export(self) -> None:
        self.transaction_service.add_transaction('expense', '2026-09-15', 5000, 'coffee', '아메리카노', ['drink'])
        csv_path = self.base_path / 'export.csv'
        count = self.csv_service.export_transactions(str(csv_path), month='2026-09')
        self.assertEqual(count, 1)
        self.assertTrue(csv_path.exists())
        with csv_path.open('r', encoding='utf-8', newline='') as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['category'], 'coffee')

    # 정상 행과 오류 행의 처리 건수를 확인한다.
    def test_csv_import(self) -> None:
        csv_path = self.base_path / 'import.csv'
        with csv_path.open('w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'type', 'category', 'amount', 'memo', 'tags'])
            writer.writerow(['2026-09-15', 'income', 'salary', '100000', '테스트 수입', 'test'])
            writer.writerow(['2026-09-15', 'expense', 'food', '-5000', '잘못된 금액', 'test'])
        imported, skipped = self.csv_service.import_transactions(str(csv_path))
        self.assertEqual(imported, 1)
        self.assertEqual(skipped, 1)
if __name__ == '__main__':
    unittest.main()
