# cli.py: 터미널 입력과 출력

`run_cli`와 입력 보조 함수는 프로젝트 정의 함수입니다. `argparse`, `input`, `print`, `Path`는 Python 표준 기능입니다. `run_cli`가 저장소와 서비스를 만들어 각 명령에 연결합니다.

## 함수와 호출 관계

| 함수 | 역할 | 프로젝트 정의 기능 호출 | Python 표준 기능 사용 |
|---|---|---|---|
| `normalize_date_input` | 빈 날짜와 숫자 날짜를 ISO 날짜로 바꾼다 | 직접 호출 없음 | `len`, `now`, `strftime` |
| `parse_amount` | 금액 문자열을 정수로 바꾸고 잘못된 입력을 안내한다 | 직접 호출 없음 | `int` |
| `choose_transaction_type` | 거래 종류를 번호로 선택받는다 | 직접 호출 없음 | `input`, `print` |
| `choose_transaction_type_for_update` | 기존 값 유지를 포함해 거래 종류를 선택받는다 | 직접 호출 없음 | `input`, `print` |
| `choose_category` | 등록된 카테고리를 번호로 선택받는다 | `iter_categories` | `enumerate`, `input`, `int`, `len`, `list`, `print` |
| `choose_category_for_update` | 기존 값 유지를 포함해 카테고리를 선택받는다 | `iter_categories` | `enumerate`, `input`, `int`, `len`, `list`, `print` |
| `build_parser` | 명령어와 옵션의 도움말 구조를 만든다 | 직접 호출 없음 | 주요 직접 호출 없음 |
| `run_cli` | 명령을 해석하고 해당 기능을 실행한다 | `BudgetRepository`, `BudgetService`, `CategoryRepository`, `CategoryService`, `CsvService`, `TransactionRepository`, `TransactionService`, `add_category`, `add_transaction`, `build_parser`, `choose_category`, `choose_category_for_update`, `choose_transaction_type`, `choose_transaction_type_for_update`, `delete_transaction`, `export_transactions`, `find_by_id`, `get_budget`, `get_budget_status`, `import_transactions`, `list_categories`, `list_transactions`, `normalize_date_input`, `parse_amount`, `remove_category`, `search_transactions`, `set_budget`, `summarize_month`, `update_transaction` | `abs`, `enumerate`, `input`, `print`, `str` |

## 흐름

`budget_app/cli.py`의 내용은 위에서 설명한 모듈과 함수에서 사용됩니다.
