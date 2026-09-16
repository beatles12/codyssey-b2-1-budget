# csv_service.py: CSV 교환

`CsvService`는 프로젝트 정의 클래스입니다. `csv.DictReader`와 `DictWriter`, `Path`, `datetime`은 Python 표준 기능입니다. CLI가 import/export에서 호출합니다.

## 함수와 호출 관계

| 함수 | 역할 | 프로젝트 정의 기능 호출 | Python 표준 기능 사용 |
|---|---|---|---|
| `CsvService.__init__` | CSV 처리에 필요한 저장소와 거래 서비스를 연결한다 | `TransactionService` | 주요 직접 호출 없음 |
| `CsvService._validate_month` | 월 입력 형식을 검사한다 | 직접 호출 없음 | `strptime` |
| `CsvService._validate_date` | 날짜 입력 형식을 검사한다 | 직접 호출 없음 | `strptime` |
| `CsvService.export_transactions` | 조건에 맞는 거래를 CSV로 내보낸다 | `_validate_date`, `_validate_month`, `iter_transactions` | `DictWriter`, `open` |
| `CsvService.import_transactions` | CSV를 행 단위로 검증해 거래를 가져온다 | `add_transaction`, `exists` | `DictReader`, `int`, `open` |

## 흐름

`budget_app/csv_service.py`의 내용은 위에서 설명한 모듈과 함수에서 사용됩니다.
