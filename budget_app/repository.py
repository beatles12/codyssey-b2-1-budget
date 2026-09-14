import json
from collections.abc import Iterator
from dataclasses import asdict
from pathlib import Path

from budget_app.models import Transaction


# ==========================================================
# [1] 거래 저장소 클래스
# ==========================================================
# 역할:
# - Transaction 거래 데이터를 파일에 저장하고 다시 불러오는 담당
# - 기본 저장 파일은 data/transactions.jsonl
# - 데이터 구조(models.py)와 파일 입출력 역할을 분리함
# ==========================================================

class TransactionRepository:

    # ======================================================
    # [1-1] 저장소 초기화
    # ======================================================
    # TransactionRepository 객체가 만들어질 때 실행됨
    # file_path를 따로 지정하지 않으면
    # data/transactions.jsonl 파일을 기본으로 사용함
    # ======================================================

    def __init__(
        self,
        file_path: str = "data/transactions.jsonl"
    ) -> None:

        # 문자열 경로를 Path 객체로 변환
        self.file_path = Path(file_path)

        # 저장 폴더가 없으면 자동 생성
        # 이미 존재하면 오류 없이 그대로 사용
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    # ======================================================
    # [2] 거래 한 건 저장
    # ======================================================
    # Transaction 객체를 딕셔너리로 바꾼 뒤
    # JSON 형태로 transactions.jsonl 파일에 저장함
    #
    # "a" = append 모드
    # 기존 내용을 지우지 않고 파일 끝에 이어서 저장함
    # ======================================================

    def add(self, transaction: Transaction) -> None:

        with self.file_path.open(
            "a",
            encoding="utf-8"
        ) as file:

            # Transaction 객체 → 딕셔너리 → JSON으로 저장
            json.dump(
                asdict(transaction),
                file,
                ensure_ascii=False
            )

            # JSONL은 거래 한 건을 한 줄에 저장하므로 줄바꿈
            file.write("\n")


    # ======================================================
    # [3] 저장된 거래 한 건씩 읽기
    # ======================================================
    # transactions.jsonl 파일을 처음부터 끝까지
    # 한꺼번에 메모리에 올리지 않고 한 줄씩 읽음
    #
    # yield를 사용해 Transaction 객체를 하나씩 반환함
    # 데이터가 많아져도 메모리를 적게 사용할 수 있음
    # ======================================================

    def iter_transactions(self) -> Iterator[Transaction]:

        # 저장 파일 자체가 없으면 읽을 거래가 없으므로 종료
        if not self.file_path.exists():
            return

        # "r" = read 모드, 파일을 읽기 전용으로 열기
        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            # 파일에서 한 줄씩 가져옴
            for line in file:

                # 빈 줄은 건너뜀
                if not line.strip():
                    continue

                # JSON 문자열 한 줄 → Python 딕셔너리로 변환
                data = json.loads(line)

                # 딕셔너리의 값을 Transaction 객체로 다시 복원
                yield Transaction(
                    id=data["id"],
                    type=data["type"],
                    date=data["date"],
                    amount=data["amount"],
                    category=data["category"],
                    memo=data.get("memo", ""),
                    tags=data.get("tags", []),
                )