# service.py: 검증과 업무 규칙

`service.py`는 사용자가 입력한 값이 올바른지 검사하고, 거래·카테고리·예산에 관한 업무 규칙을 처리하는 모듈입니다.

`TransactionService`, `CategoryService`, `BudgetService`는 이번 프로젝트에서 직접 만든 클래스입니다.

Python 표준 라이브러리에서는 `calendar.monthrange`, `collections.defaultdict`, `collections.deque`, `collections.abc.Iterator`, `uuid.uuid4`를 사용합니다.

CLI와 CSV 서비스는 이 서비스 계층을 호출하고, 서비스는 Repository를 통해 실제 JSONL 파일을 읽거나 저장합니다.

## 모듈 수준 함수

| 함수 | 종류 | 역할 | 누가 호출하는가 | 다음에 사용하는 기능 |
| --- | --- | --- | --- | --- |
| `_is_valid_date` | 프로젝트 함수 | `YYYY-MM-DD` 형식과 실제 존재하는 날짜인지 검사한다 | `TransactionService`, `CsvService` | `monthrange`, `split`, `isdigit`, `map`, `int` |
| `_is_valid_month` | 프로젝트 함수 | `YYYY-MM` 형식과 실제 월 범위인지 검사한다 | `TransactionService`, `BudgetService`, `CsvService` | `split`, `isdigit`, `map`, `int` |

`monthrange()`는 Python 표준 라이브러리 `calendar`가 제공하는 함수입니다. 해당 연도와 월의 마지막 날짜를 알려주기 때문에 2월 30일처럼 실제로 존재하지 않는 날짜를 걸러낼 수 있습니다.

## TransactionService

거래 추가, 조회, 검색, 요약, 수정, 삭제를 담당합니다.

| 함수 | 역할 | 누가 호출하는가 | 다음에 호출하는 프로젝트 기능 | Python 기능 |
| --- | --- | --- | --- | --- |
| `__init__` | 거래 저장소를 서비스에 연결한다 | CLI, CSV 서비스 | `TransactionRepository` | 주요 직접 호출 없음 |
| `get_transaction_validation_error` | 거래 종류, 날짜, 금액, 카테고리를 검사하고 오류 메시지를 돌려준다 | `add_transaction`, `update_transaction`, `CsvService` | `_is_valid_date` | `strip` |
| `_validate_search_date` | 검색에 사용하는 날짜를 검사한다 | `search_transactions` | `_is_valid_date` | `raise ValueError` |
| `_validate_month` | 월 요약에 사용하는 월을 검사한다 | `summarize_month` | `_is_valid_month` | `raise ValueError` |
| `add_transaction` | 거래를 검증하고 UUID를 만든 뒤 저장한다 | CLI, CSV 서비스 | `get_transaction_validation_error`, `Transaction`, `repository.add` | `uuid4` |
| `list_transactions` | 최근 거래를 지정한 개수만큼 최신순으로 돌려준다 | CLI | `repository.iter_transactions` | `deque`, `list`, `reversed` |
| `search_transactions` | 조건에 맞는 거래를 찾아 최신순으로 하나씩 `yield`한다 | CLI | `_validate_search_date`, `repository.iter_transactions` | `deque`, `yield`, `lower` |
| `summarize_month` | 월별 수입·지출·잔액과 상위 지출 카테고리를 계산한다 | CLI | `_validate_month`, `repository.iter_transactions` | `defaultdict`, `sorted` |
| `update_transaction` | 기존 거래를 찾고 변경값을 검증한 뒤 수정한다 | CLI | `find_by_id`, `get_transaction_validation_error`, `Transaction`, `update_by_id` | `strip` |
| `delete_transaction` | ID로 거래를 찾아 삭제한다 | CLI | `find_by_id`, `delete_by_id` | `strip` |

### add_transaction 호출 흐름

사용자 입력  
→ CLI  
→ `TransactionService.add_transaction()`  
→ `get_transaction_validation_error()`  
→ `_is_valid_date()`  
→ `uuid4()`  
→ `Transaction` 생성  
→ `TransactionRepository.add()`  
→ `transactions.jsonl`

### list_transactions와 deque

`deque(maxlen=limit)`는 최근 거래만 일정 개수 보관하기 위해 사용합니다.

예를 들어 `limit=20`이면 파일 전체를 읽더라도 메모리에는 최근 20건만 유지합니다.

그래서 거래 파일 전체를 한꺼번에 `list`로 만드는 것보다 메모리를 적게 사용할 수 있습니다.

### search_transactions와 Generator

`search_transactions()`는 `yield`를 사용하는 Generator 함수입니다.

`yield`는 결과를 한꺼번에 모두 반환하는 대신 필요한 값을 하나씩 전달할 수 있게 하는 Python 문법입니다.

현재 구현은 파일 자체는 `iter_transactions()`로 한 줄씩 읽습니다. 다만 검색 결과를 최신순으로 보여주기 위해 일치하는 거래를 `deque`에 모은 뒤 뒤에서부터 `yield`합니다.

따라서 검색 결과가 매우 많으면 일치한 거래 수만큼 메모리를 사용할 수 있습니다.

## CategoryService

카테고리 조회, 추가, 삭제를 담당합니다.

| 함수 | 역할 | 누가 호출하는가 | 다음에 호출하는 프로젝트 기능 | Python 기능 |
| --- | --- | --- | --- | --- |
| `__init__` | 카테고리 저장소와 거래 저장소를 연결한다 | CLI | `CategoryRepository`, `TransactionRepository` | 주요 직접 호출 없음 |
| `list_categories` | 등록된 카테고리를 목록으로 돌려준다 | CLI | `iter_categories` | `list` |
| `add_category` | 빈 값과 중복 여부를 확인하고 카테고리를 추가한다 | CLI | `exists`, `add` | `strip` |
| `remove_category` | 존재 여부와 사용 중 여부를 확인하고 삭제한다 | CLI | `exists`, `iter_transactions`, `remove` | `strip` |

카테고리를 삭제하기 전에 모든 거래를 확인하는 이유는 이미 사용 중인 카테고리를 지워서 기존 거래 정보가 어긋나는 것을 막기 위해서입니다.

## BudgetService

월 예산 저장과 예산 사용 현황 계산을 담당합니다.

| 함수 | 역할 | 누가 호출하는가 | 다음에 호출하는 프로젝트 기능 | Python 기능 |
| --- | --- | --- | --- | --- |
| `__init__` | 예산 저장소를 서비스에 연결한다 | CLI | `BudgetRepository` | 주요 직접 호출 없음 |
| `_validate_budget` | 월 형식과 예산 금액을 검사한다 | `set_budget` | `_is_valid_month` | `raise ValueError` |
| `set_budget` | 검증한 월 예산을 저장한다 | CLI | `_validate_budget`, `repository.set_budget` | 주요 직접 호출 없음 |
| `get_budget` | 월을 검사하고 저장된 예산을 읽는다 | CLI, `get_budget_status` | `_is_valid_month`, `repository.get_budget` | `raise ValueError` |
| `get_budget_status` | 사용률, 남은 금액, 초과 여부를 계산한다 | CLI | `get_budget` | 산술 연산 |

## Python 기능과 프로젝트 기능 구분

### Python 기본 함수

- `len()`
- `all()`
- `map()`
- `int()`
- `list()`
- `reversed()`
- `sorted()`

### Python 표준 라이브러리

- `calendar.monthrange`
- `collections.defaultdict`
- `collections.deque`
- `collections.abc.Iterator`
- `uuid.uuid4`

### Python 문법과 개념

- `class`
- `def`
- `raise`
- `yield`
- Type Hint
- `str | None`
- `list[str]`

### 프로젝트에서 직접 만든 기능

- `Transaction`
- `TransactionService`
- `CategoryService`
- `BudgetService`
- `TransactionRepository`
- `CategoryRepository`
- `BudgetRepository`
- `_is_valid_date`
- `_is_valid_month`
- `get_transaction_validation_error`

## 전체 역할

`service.py`는 직접 파일 형식을 관리하는 곳이 아닙니다.

서비스는

사용자 요청  
→ 값 검증  
→ 업무 규칙 처리  
→ Repository 호출

순서로 동작합니다.

실제 JSONL 파일 읽기와 쓰기는 `repository.py`가 담당합니다.

이렇게 역할을 나누면 CLI 화면이 바뀌더라도 핵심 업무 규칙을 다시 만들 필요가 없고, 저장 방식이 바뀌어도 서비스 로직을 최대한 유지할 수 있습니다.