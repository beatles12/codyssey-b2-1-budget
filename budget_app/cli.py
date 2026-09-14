import argparse
from datetime import datetime

from budget_app.repository import (
    CategoryRepository,
    TransactionRepository,
)
from budget_app.service import (
    CategoryService,
    TransactionService,
)


# ==========================================================
# [1] 날짜 입력 편하게 바꾸기
# ==========================================================
# 역할:
# - Enter만 누르면 오늘 날짜 사용
# - 20260914처럼 숫자 8자리로 입력하면
#   2026-09-14 형식으로 자동 변환
# ==========================================================

def normalize_date_input(date_text: str) -> str:

    if not date_text:
        return datetime.now().strftime("%Y-%m-%d")

    if (
        len(date_text) == 8
        and date_text.isdigit()
    ):
        return (
            f"{date_text[:4]}-"
            f"{date_text[4:6]}-"
            f"{date_text[6:]}"
        )

    return date_text


# ==========================================================
# [2] 거래 종류 번호 선택
# ==========================================================

def choose_transaction_type() -> str:

    print("\n[거래 종류 선택]")
    print("1. income  (수입)")
    print("2. expense (지출)")

    while True:

        choice = input(
            "번호 선택: "
        ).strip()

        if choice == "1":
            return "income"

        if choice == "2":
            return "expense"

        print(
            "1 또는 2를 입력해주세요."
        )


# ==========================================================
# [3] 카테고리 번호 선택
# ==========================================================

def choose_category(
    category_repository: CategoryRepository
) -> str:

    categories = list(
        category_repository.iter_categories()
    )

    print("\n[카테고리 선택]")

    for number, category in enumerate(
        categories,
        start=1
    ):
        print(
            f"{number}. {category}"
        )

    while True:

        choice = input(
            "번호 선택: "
        ).strip()

        try:
            number = int(choice)

            if 1 <= number <= len(categories):
                return categories[number - 1]

        except ValueError:
            pass

        print(
            "목록에 있는 번호를 입력해주세요."
        )


# ==========================================================
# [4] 명령어 프로그램(CLI) 시작
# ==========================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="나만의 용돈 기입장 프로그램"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )


    # ======================================================
    # [5] add 명령어 등록
    # ======================================================

    subparsers.add_parser(
        "add",
        help="새 거래 추가"
    )


    # ======================================================
    # [6] list 명령어 등록
    # ======================================================

    list_parser = subparsers.add_parser(
        "list",
        help="저장된 거래 목록 조회"
    )

    list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="출력할 최대 거래 수 (기본값: 20)"
    )


    # ======================================================
    # [7] delete 명령어 등록
    # ======================================================
    # 실행 예:
    # python -m budget_app delete --id 거래ID
    # ======================================================

    delete_parser = subparsers.add_parser(
        "delete",
        help="거래 삭제"
    )

    delete_parser.add_argument(
        "--id",
        required=True,
        help="삭제할 거래 id"
    )


    # ======================================================
    # [8] category 명령어 등록
    # ======================================================

    category_parser = subparsers.add_parser(
        "category",
        help="카테고리 관리"
    )

    category_subparsers = (
        category_parser.add_subparsers(
            dest="category_command"
        )
    )

    category_subparsers.add_parser(
        "list",
        help="카테고리 목록 조회"
    )

    category_subparsers.add_parser(
        "add",
        help="새 카테고리 추가"
    )

    category_subparsers.add_parser(
        "remove",
        help="카테고리 삭제"
    )


    # ======================================================
    # [9] 사용자가 입력한 명령어 읽기
    # ======================================================

    args = parser.parse_args()


    # ======================================================
    # [10] Repository와 Service 준비
    # ======================================================

    transaction_repository = (
        TransactionRepository()
    )

    category_repository = (
        CategoryRepository()
    )

    transaction_service = (
        TransactionService(
            transaction_repository
        )
    )

    category_service = (
        CategoryService(
            category_repository,
            transaction_repository,
        )
    )


    # ======================================================
    # [11] add 명령어 실행
    # ======================================================

    if args.command == "add":

        try:

            date_text = input(
                "날짜(Enter=오늘 / 예: 20260914): "
            ).strip()

            date = normalize_date_input(
                date_text
            )

            transaction_type = (
                choose_transaction_type()
            )

            category = choose_category(
                category_repository
            )

            amount_text = input(
                "금액(양수): "
            ).strip()

            amount = int(
                amount_text
            )

            memo = input(
                "메모(선택): "
            ).strip()

            tags_text = input(
                "태그(쉼표 구분 / 없으면 Enter): "
            ).strip()

            if tags_text:

                tags = [
                    tag.strip()
                    for tag in tags_text.split(",")
                    if tag.strip()
                ]

            else:

                tags = []

            transaction = (
                transaction_service.add_transaction(
                    transaction_type=transaction_type,
                    date=date,
                    amount=amount,
                    category=category,
                    memo=memo,
                    tags=tags,
                )
            )

            print(
                f"\n[저장 완료] id={transaction.id}"
            )

        except ValueError as error:

            print(
                f"\n[입력 오류] {error}"
            )

            raise SystemExit(1)

        return


    # ======================================================
    # [12] list 명령어 실행
    # ======================================================
    # 거래 내용과 함께 id도 표시함
    # delete / update에서 이 id를 사용함
    # ======================================================

    if args.command == "list":

        try:

            transactions = (
                transaction_service.list_transactions(
                    limit=args.limit
                )
            )

        except ValueError as error:

            print(
                f"[입력 오류] {error}"
            )

            raise SystemExit(1)

        if not transactions:

            print(
                "저장된 거래가 없습니다."
            )

            return

        for number, transaction in enumerate(
            transactions,
            start=1
        ):

            print(
                f"\n[{number}] "
                f"{transaction.date} | "
                f"{transaction.type} | "
                f"{transaction.category} | "
                f"{transaction.amount:,}원 | "
                f"{transaction.memo}"
            )

            print(
                f"    id: {transaction.id}"
            )

        return


    # ======================================================
    # [13] delete 명령어 실행
    # ======================================================
    # --id로 받은 거래 id를 삭제함
    # 실제 삭제 전에 한 번 더 사용자에게 확인함
    # ======================================================

    if args.command == "delete":

        answer = input(
            f"id={args.id}\n"
            "이 거래를 삭제할까요? (y/N): "
        ).strip().lower()

        if answer != "y":

            print(
                "삭제를 취소했습니다."
            )

            return

        try:

            transaction_service.delete_transaction(
                args.id
            )

            print(
                "[삭제 완료]"
            )

        except ValueError as error:

            print(
                f"[삭제 오류] {error}"
            )

            raise SystemExit(1)

        return


    # ======================================================
    # [14] category 명령어 실행
    # ======================================================

    if args.command == "category":

        # ----------------------------------------------
        # category list
        # ----------------------------------------------

        if args.category_command == "list":

            categories = (
                category_service.list_categories()
            )

            print("\n[카테고리 목록]")

            for number, category in enumerate(
                categories,
                start=1
            ):
                print(
                    f"{number}. {category}"
                )

            return


        # ----------------------------------------------
        # category add
        # ----------------------------------------------

        if args.category_command == "add":

            category_name = input(
                "추가할 카테고리 이름: "
            ).strip()

            try:

                category_service.add_category(
                    category_name
                )

                print(
                    f"[추가 완료] {category_name}"
                )

            except ValueError as error:

                print(
                    f"[입력 오류] {error}"
                )

                raise SystemExit(1)

            return


        # ----------------------------------------------
        # category remove
        # ----------------------------------------------

        if args.category_command == "remove":

            category_name = choose_category(
                category_repository
            )

            answer = input(
                f"'{category_name}'을 삭제할까요? (y/N): "
            ).strip().lower()

            if answer != "y":

                print(
                    "삭제를 취소했습니다."
                )

                return

            try:

                category_service.remove_category(
                    category_name
                )

                print(
                    f"[삭제 완료] {category_name}"
                )

            except ValueError as error:

                print(
                    f"[삭제 오류] {error}"
                )

                raise SystemExit(1)

            return


        category_parser.print_help()
        return


    # ======================================================
    # [15] 명령어가 없으면 도움말 출력
    # ======================================================

    parser.print_help()