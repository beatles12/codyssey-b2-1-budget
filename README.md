# B2-1 나만의 용돈 기입장 프로그램

Python 표준 라이브러리만 사용하여 만든 파일 기반 CLI 용돈 기입장 프로그램입니다.

거래 내역을 추가·조회·검색·수정·삭제할 수 있고,
월별 요약, 예산 관리, 카테고리 관리,
CSV 가져오기/내보내기 기능을 제공합니다.

---

## 1. 개발 환경

- Python 3.10 이상
- 개발 환경: Python 3.14.6
- 외부 라이브러리 사용 없음
- Python 표준 라이브러리만 사용

---

## 2. 실행 방법

프로젝트 최상위 폴더에서 실행합니다.

```powershell
python -m budget_app --help
```

기본 실행 형식:

```text
python -m budget_app <command> [options]
```

위의 `<command>`와 `[options]`는 설명용 표기이며
PowerShell에 그대로 입력하는 문장이 아닙니다.

예를 들어 거래 목록 3건을 보려면 다음과 같이 실행합니다.

```powershell
python -m budget_app list --limit 3
```

---

## 3. 주요 명령

### 거래 추가

```powershell
python -m budget_app add
```

날짜, 거래 종류, 카테고리, 금액, 메모, 태그를
대화형으로 입력합니다.

날짜는 다음 방식으로 입력할 수 있습니다.

- Enter: 오늘 날짜
- 20260915
- 2026-09-15

저장이 완료되면 생성된 거래 id가 출력됩니다.

---

### 거래 목록 조회

```powershell
python -m budget_app list --limit 3
```

최근 거래부터 출력합니다.

---

### 거래 검색

카테고리 검색:

```powershell
python -m budget_app search --category food
```

기간 검색:

```powershell
python -m budget_app search --from 2026-09-01 --to 2026-09-30
```

타입 검색:

```powershell
python -m budget_app search --type expense
```

메모 검색:

```powershell
python -m budget_app search --q 점심
```

태그 검색:

```powershell
python -m budget_app search --tag meal
```

검색 결과는 최신순으로 출력합니다.

---

### 월별 요약

```powershell
python -m budget_app summary --month 2026-09 --top 3
```

다음 내용을 출력합니다.

- 총 수입
- 총 지출
- 잔액
- 지출 카테고리 TOP N
- 예산 사용률
- 남은 예산 또는 예산 초과 금액

해당 월에 거래가 없으면 `데이터 없음`을 출력합니다.

---

### 거래 수정

이 프로젝트의 update 기능은
**대화형 방식으로 고정**했습니다.

먼저 거래 id를 확인합니다.

```powershell
python -m budget_app list --limit 3
```

그다음 실제 거래 id를 사용합니다.

```powershell
python -m budget_app update --id 실제거래ID
```

`실제거래ID`는 설명용 표현입니다.
`<거래ID>` 같은 문자를 그대로 입력하지 않습니다.

수정할 값만 새로 입력하고,
기존 값을 유지하려면 Enter를 누릅니다.

---

### 거래 삭제

```powershell
python -m budget_app delete --id 실제거래ID
```

존재하지 않는 id를 입력하면 오류 메시지를 출력합니다.

---

## 4. 카테고리 관리

카테고리 목록:

```powershell
python -m budget_app category list
```

카테고리 추가:

```powershell
python -m budget_app category add
```

카테고리 삭제:

```powershell
python -m budget_app category remove
```

현재 거래에서 사용 중인 카테고리는 삭제할 수 없습니다.

---

## 5. 예산 관리

월 예산 설정:

```powershell
python -m budget_app budget set --month 2026-09 --amount 600000
```

월 예산 조회:

```powershell
python -m budget_app budget get --month 2026-09
```

예산이 설정된 달의 summary에서는
예산 사용률과 초과 여부를 함께 확인할 수 있습니다.

---

## 6. 데이터 저장 위치와 형식

기본 저장 폴더:

```text
./data
```

기본 저장 파일:

```text
data/transactions.jsonl
data/categories.jsonl
data/budgets.jsonl
```

세 파일 모두 JSONL 형식을 사용합니다.

JSONL은 한 줄에 JSON 객체 하나를 저장하는 형식입니다.

예:

```json
{"id":"abc","type":"expense","date":"2026-09-15","amount":15000,"category":"food","memo":"점심","tags":["meal"]}
```

프로그램을 종료하고 다시 실행해도
파일에 저장된 거래, 카테고리, 예산 데이터는 유지됩니다.

---

## 7. 데이터 저장 폴더 변경

기본 `data` 폴더 대신 다른 폴더를 사용할 수 있습니다.

`--data-dir`은 command 앞에 사용합니다.

예:

```powershell
python -m budget_app --data-dir test_data category list
```

이 경우 데이터는 `test_data` 폴더에 저장됩니다.

---

## 8. CSV 내보내기

월 기준 export:

```powershell
python -m budget_app export --out export.csv --month 2026-09
```

기간 기준 export:

```powershell
python -m budget_app export --out export.csv --from 2026-09-01 --to 2026-09-30
```

export는 다음 중 하나의 조건이 반드시 필요합니다.

- `--month YYYY-MM`
- `--from YYYY-MM-DD --to YYYY-MM-DD`

---

## 9. CSV 가져오기

실제 존재하는 CSV 파일을 지정해야 합니다.

예:

```powershell
python -m budget_app import --from import_test.csv
```

가져오기 결과는 다음처럼 처리 건수를 출력합니다.

```text
[완료] imported=1, skipped=1
```

잘못된 행이 있어도 전체 import를 중단하지 않고
해당 행만 skipped 처리합니다.

---

## 10. CSV 스키마

CSV 파일은 UTF-8, 헤더 포함 형식을 사용합니다.

필드 순서:

```text
date,type,category,amount,memo,tags
```

| column | 필수 | 설명 |
|---|---|---|
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 0보다 큰 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표로 구분한 문자열 |

---

## 11. 프로젝트 구조

```text
budget_app/
├── __init__.py
├── __main__.py
├── cli.py
├── csv_service.py
├── decorators.py
├── models.py
├── repository.py
└── service.py

data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl

tests/
└── test_budget_app.py
```

주요 역할:

- `models.py`: 거래 데이터 구조 정의
- `repository.py`: JSONL 파일 저장과 읽기
- `service.py`: 검증과 업무 규칙 처리
- `cli.py`: 명령어와 사용자 입력/출력 처리
- `csv_service.py`: CSV import/export 처리
- `decorators.py`: 공통 기능 데코레이터
- `tests/`: 자동 테스트

---

## 12. 제너레이터

`TransactionRepository.iter_transactions()`는
`yield`를 사용하여 거래를 한 줄씩 읽습니다.

파일 전체를 한 번에 메모리에 올리지 않고
필요한 데이터를 순서대로 처리할 수 있습니다.

`list`는 `deque(maxlen=limit)`를 사용하여
필요한 최근 거래 수만 메모리에 유지합니다.

검색도 Repository에서는 한 줄씩 읽지만,
현재 구현은 최신순 출력을 위해 검색 결과를
`deque`에 모은 뒤 역순으로 출력합니다.

따라서 검색 결과가 매우 많아질 경우에는
추가적인 메모리를 사용할 수 있다는 한계가 있습니다.

---

## 13. 데코레이터

`decorators.py`의 `safe_entry`를 `__main__.py`의 `main()`에 한 번 적용했습니다.
입력 오류, 입력 중단, 파일 오류를 같은 방식으로 안내하고
실패 시 종료 코드 1을 반환합니다.

CSV 가져오기의 행 단위 예외 처리는 한 행이 잘못되어도
다음 행을 계속 처리해야 하는 요구사항 때문에 남겼습니다.
이 결정의 기준은 `docs/DEVELOPMENT_RULES.md`에 설명했습니다.

---

## 14. 타입 힌트

함수의 입력값과 반환값에 타입 힌트를 적용했습니다.

예:

```python
def get_budget(
    self,
    month: str
) -> int | None:
```

이 코드는 `month`가 문자열이며,
결과는 정수 또는 `None`일 수 있다는 뜻입니다.

타입 힌트는 Python 실행 자체를 강제로 제한하는 기능이 아니라,
코드의 입출력 계약을 사람이 쉽게 이해하고
IDE와 정적 분석 도구가 오류를 찾기 쉽게 해주는 역할을 합니다.

---

## 15. 오류 처리

잘못된 입력에서는 긴 Python traceback을 사용자에게 노출하지 않고
원인과 해결 힌트를 출력하도록 처리했습니다.

오류 발생 시 `SystemExit(1)`을 사용하여
0이 아닌 종료 코드로 프로그램을 종료합니다.

정상 실행은 종료 코드 0,
오류 실행은 0이 아닌 종료 코드가 됩니다.

---

## 16. 자동 테스트

자동 테스트 실행:

```powershell
python -m unittest discover -s tests -v
```

코드 읽기 규칙과 파일별 함수 설명은 `docs/` 폴더에 있습니다.

테스트 항목에는 다음 기능이 포함됩니다.

- 거래 추가/목록
- 잘못된 금액 검증
- 검색
- 월별 요약
- 수정
- 삭제
- 카테고리 추가/삭제
- 사용 중 카테고리 삭제 방지
- 예산 저장/조회
- 예산 사용률
- CSV export
- CSV import

---

## 17. 사용한 주요 표준 라이브러리

- `argparse`
- `csv`
- `json`
- `pathlib`
- `dataclasses`
- `datetime`
- `uuid`
- `collections`
- `typing`
- `unittest`
- `tempfile`

외부 패키지는 사용하지 않았습니다.

---

## 18. JSONL을 내부 저장 형식으로 선택한 이유

이 프로젝트는 프로그램 내부 영구 저장 형식으로 JSONL을 사용하고,
외부 데이터 교환 형식으로 CSV를 사용합니다.

| 항목 | JSONL | CSV |
|---|---|---|
| 구조 | 한 줄에 JSON 객체 하나 | 행과 열 형태 |
| Python 객체 표현 | 비교적 자연스러움 | 모든 값을 표 형태로 변환해야 함 |
| 리스트 저장 | tags 같은 리스트를 그대로 표현하기 쉬움 | 쉼표 문자열 등으로 변환 필요 |
| 한 줄씩 읽기 | 쉬움 | 쉬움 |
| 사람이 표로 보기 | CSV보다 불편 | 매우 편함 |
| Excel 등과 교환 | 불편 | 편함 |
| 이 프로젝트에서의 용도 | 내부 영구 저장 | import / export |

### JSONL을 선택한 이유

거래 한 건이 `Transaction` 객체와 비슷한 구조를 가지며,
`tags`처럼 리스트 형태의 값도 포함하기 때문에 JSON과 잘 맞습니다.

또한 JSONL은 한 줄에 거래 한 건을 저장하므로
`iter_transactions()`에서 파일을 한 줄씩 읽는
제너레이터 방식과 연결하기 쉽습니다.

CSV는 사람이 표 형태로 확인하거나
다른 프로그램과 데이터를 주고받기 편하기 때문에
import/export 형식으로 사용했습니다.

---

## 19. 거래가 10만 건 이상으로 늘어날 경우

현재 프로그램은 파일 기반으로 동작하므로
데이터가 매우 많아지면 다음 부분이 병목이 될 수 있습니다.

### 1. 검색

현재는 원하는 거래를 찾기 위해
`transactions.jsonl`을 처음부터 끝까지 확인할 수 있습니다.

거래가 10만 건이라면 검색 한 번에
최대 10만 건을 검사할 수 있습니다.

개선 방법:

- 날짜나 카테고리 기준 인덱스 사용
- SQLite 같은 데이터베이스로 변경
- 검색 결과를 페이지 단위로 조회

### 2. search의 최신순 출력

Repository에서는 거래를 제너레이터로 한 줄씩 읽지만,
현재 `search_transactions()`는 검색 결과를 최신순으로 출력하기 위해
일치한 결과를 `deque`에 모은 뒤 역순으로 반환합니다.

따라서 검색 결과가 많으면
검색 결과 수만큼 메모리 사용량이 증가할 수 있습니다.

개선 방법:

- 파일을 역방향으로 읽는 구조 적용
- 검색 결과에 페이지 크기 또는 limit 적용
- 데이터베이스의 ORDER BY와 LIMIT 사용

### 3. update / delete

JSONL 파일에서 거래 하나를 수정하거나 삭제할 때
안전성을 위해 전체 파일을 임시 파일로 다시 작성합니다.

거래 수가 많아질수록 파일 전체를 다시 쓰는 시간이 증가합니다.

개선 방법:

- SQLite 같은 데이터베이스에서 id 기반 수정/삭제
- id 인덱스를 이용해 탐색 비용 감소

### 현재 구조를 사용한 이유

이번 미션은 파일 입출력과 JSONL,
제너레이터, 서비스/저장소 구조를 학습하는 것이 목적이므로
현재 규모에서는 파일 기반 구조를 사용했습니다.

데이터 규모가 크게 증가한다면
SQLite 또는 데이터베이스 기반 저장소로 교체하는 것이
우선적인 개선 방향입니다.
