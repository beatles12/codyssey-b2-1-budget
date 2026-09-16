# repository.py: 파일 저장과 읽기

`TransactionRepository`, `CategoryRepository`, `BudgetRepository`는 프로젝트 정의 클래스입니다. `json`, `pathlib.Path`, `dataclasses.asdict`는 Python 표준 기능입니다. 서비스가 이 저장소들을 호출합니다.

## 함수와 호출 관계

| 함수 | 역할 | 프로젝트 정의 기능 호출 | Python 표준 기능 사용 |
|---|---|---|---|
| `_write_json_line` | 한 항목을 JSONL 한 줄로 저장한다 | 직접 호출 없음 | `dump` |
| `TransactionRepository.__init__` | 저장 파일 경로를 준비한다 | 직접 호출 없음 | 주요 직접 호출 없음 |
| `TransactionRepository.add` | 새 항목을 JSONL 파일에 추가한다 | `_write_json_line` | `asdict`, `open` |
| `TransactionRepository.iter_transactions` | 거래를 파일에서 한 건씩 읽는다 | `Transaction`, `exists` | `loads`, `open` |
| `TransactionRepository.find_by_id` | ID와 일치하는 거래를 찾는다 | `iter_transactions` | 주요 직접 호출 없음 |
| `TransactionRepository.update_by_id` | 거래 파일을 다시 써서 지정한 거래를 수정한다 | `_write_json_line`, `iter_transactions` | `asdict`, `open` |
| `TransactionRepository.delete_by_id` | 거래 파일을 다시 써서 지정한 거래를 삭제한다 | `_write_json_line`, `iter_transactions` | `asdict`, `open` |
| `CategoryRepository.__init__` | 저장 파일 경로를 준비한다 | `_create_default_categories`, `exists` | 주요 직접 호출 없음 |
| `CategoryRepository._create_default_categories` | 처음 사용할 기본 카테고리를 저장한다 | `_write_json_line` | `open` |
| `CategoryRepository.iter_categories` | 카테고리를 파일에서 한 건씩 읽는다 | `exists` | `loads`, `open` |
| `CategoryRepository.exists` | 카테고리의 등록 여부를 확인한다 | `iter_categories` | 주요 직접 호출 없음 |
| `CategoryRepository.add` | 새 항목을 JSONL 파일에 추가한다 | `_write_json_line` | `open` |
| `CategoryRepository.remove` | 지정한 카테고리를 파일에서 제거한다 | `_write_json_line`, `iter_categories` | `list`, `open` |
| `BudgetRepository.__init__` | 저장 파일 경로를 준비한다 | 직접 호출 없음 | 주요 직접 호출 없음 |
| `BudgetRepository.iter_budgets` | 예산을 파일에서 한 건씩 읽는다 | `exists` | `loads`, `open` |
| `BudgetRepository.get_budget` | 해당 월의 예산을 찾는다 | `iter_budgets` | 주요 직접 호출 없음 |
| `BudgetRepository.set_budget` | 해당 월의 예산을 저장하거나 덮어쓴다 | `_write_json_line`, `iter_budgets` | `open` |

## 흐름

`budget_app/repository.py`의 내용은 위에서 설명한 모듈과 함수에서 사용됩니다.
