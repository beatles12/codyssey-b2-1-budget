# test_budget_app.py: 자동 검증

`BudgetAppTestCase`의 메서드는 프로젝트 테스트입니다. `unittest`, `tempfile`, `csv`, `Path`는 Python 표준 기능입니다. 각 테스트는 임시 폴더에서 서비스를 호출합니다.

## 함수와 호출 관계

| 함수 | 역할 | 프로젝트 정의 기능 호출 | Python 표준 기능 사용 |
|---|---|---|---|
| `BudgetAppTestCase.setUp` | 테스트마다 별도 임시 저장소를 만든다 | `BudgetRepository`, `BudgetService`, `CategoryRepository`, `CategoryService`, `CsvService`, `TransactionRepository`, `TransactionService` | `TemporaryDirectory`, `str` |
| `BudgetAppTestCase.tearDown` | 테스트 임시 저장소를 정리한다 | 직접 호출 없음 | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_add_and_list_transactions` | 거래 추가와 최근 목록을 확인한다 | `add_transaction`, `list_transactions` | `len` |
| `BudgetAppTestCase.test_invalid_amount` | 0원 거래 거부를 확인한다 | `add_transaction` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_search_by_category` | 카테고리 검색을 확인한다 | `add_transaction`, `search_transactions` | `len`, `list` |
| `BudgetAppTestCase.test_monthly_summary` | 월별 수입과 지출 계산을 확인한다 | `add_transaction`, `summarize_month` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_update_transaction` | 거래 수정과 파일 저장을 확인한다 | `add_transaction`, `find_by_id`, `update_transaction` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_delete_transaction` | 거래 삭제를 확인한다 | `add_transaction`, `delete_transaction`, `find_by_id` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_category_add_and_remove` | 카테고리 추가와 삭제를 확인한다 | `add_category`, `exists`, `remove_category` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_category_in_use_cannot_be_removed` | 사용 중인 카테고리 삭제 방지를 확인한다 | `add_transaction`, `remove_category` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_budget_set_and_get` | 예산 저장과 조회를 확인한다 | `get_budget`, `set_budget` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_budget_status` | 예산 사용률을 확인한다 | `get_budget_status`, `set_budget` | 주요 직접 호출 없음 |
| `BudgetAppTestCase.test_csv_export` | CSV 내보내기 결과를 확인한다 | `add_transaction`, `exists`, `export_transactions` | `DictReader`, `len`, `list`, `open`, `str` |
| `BudgetAppTestCase.test_csv_import` | 정상 행과 오류 행의 처리 건수를 확인한다 | `import_transactions` | `open`, `str`, `writer` |

## 흐름

`tests/test_budget_app.py`의 내용은 위에서 설명한 모듈과 함수에서 사용됩니다.
