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
# [3] 수정용 거래 종류 선택
# ==========================================================
# Enter를 누르면 기존 값을 그대로 유지함
# ==========================================================

def choose_transaction_type_for_update(
    current_type: str
) -> str | None:

    print(
        f"\n현재 거래 종류: {current_type}"
    )

    print("1. income  (수입)")
    print("2. expense (지출)")
    print("Enter. 기존 값 유지")

    while True:

        choice = input(
            "번호 선택: "
        ).strip()

        if choice == "":
            return None

        if choice == "1":
            return "income"

        if choice == "2":
            return "expense"

        print(
            "1, 2 또는 Enter를 입력해주세요."
        )


# ==========================================================
# [4] 카테고리 번호 선택
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
# [5] 수정용 카테고리 선택
# ==========================================================
# Enter를 누르면 기존 카테고리를 유지함
# ==========================================================

def choose_category_for_update(
    category_repository: CategoryRepository,
    current_category: str,
) -> str | None:

    categories = list(
        category_repository.iter_categories()
    )

    print(
        f"\n현재 카테고리: {current_category}"
    )

    for number, category in enumerate(
        categories,
        start=1
    ):
        print(
            f"{number}. {category}"
        )

    print("Enter. 기존 값 유지")

    while True:

        choice = input(
            "번호 선택: "
        ).strip()

        if choice == "":
            return None

        try:
            number = int(choice)

            if 1 <= number <= len(categories):
                return categories[number - 1]

        except ValueError:
            pass

        print(
            "목록 번호 또는 Enter를 입력해주세요."
        )


# ==========================================================
# [6] 명령어 프로그램(CLI) 시작
# ==========================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="나만의 용돈 기입장 프로그램"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )


    # ======================================================
    # [7] add 명령어 등록
    # ======================================================

    subparsers.add_parser(
        "add",
        help="새 거래 추가"
    )


    # ======================================================
    # [8] list 명령어 등록
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
    # [9] update 명령어 등록
    # ======================================================
    # 실행 예:
    # python -m budget_app update --id 거래ID
    # ======================================================

    update_parser = subparsers.add_parser(
        "update",
        help="기존 거래 수정"
    )

    update_parser.add_argument(
        "--id",
        required=True,
        help="수정할 거래 id"
    )


    # ======================================================
    # [10] delete 명령어 등록
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
    # [11] category 명령어 등록
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
    # [12] 사용자가 입력한 명령어 읽기
    # ======================================================

    args = parser.parse_args()


    # ======================================================
    # [13] Repository와 Service 준비
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
    # [14] add 명령어 실행
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
    # [15] list 명령어 실행
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
    # [16] update 명령어 실행
    # ======================================================
    # 기존 거래를 먼저 찾고 현재 값을 보여줌
    #
    # Enter:
    # - 기존 값 유지
    #
    # 새 값을 입력:
    # - 해당 항목만 수정
    # ======================================================

    if args.command == "update":

        current = transaction_repository.find_by_id(
            args.id
        )

        if current is None:

            print(
                "[수정 오류] 해당 id의 거래를 찾을 수 없습니다."
            )

            raise SystemExit(1)

        print("\n[현재 거래]")
        print(
            f"날짜: {current.date}"
        )
        print(
            f"종류: {current.type}"
        )
        print(
            f"카테고리: {current.category}"
        )
        print(
            f"금액: {current.amount:,}원"
        )
        print(
            f"메모: {current.memo}"
        )
        print(
            f"태그: {', '.join(current.tags)}"
        )

        print(
            "\n바꾸지 않을 항목은 Enter를 누르세요."
        )


        # ----------------------------------------------
        # 날짜 수정
        # ----------------------------------------------

        date_text = input(
            f"새 날짜 [{current.date}]: "
        ).strip()

        if date_text:

            new_date = normalize_date_input(
                date_text
            )

        else:

            new_date = None


        # ----------------------------------------------
        # 거래 종류 수정
        # ----------------------------------------------

        new_type = (
            choose_transaction_type_for_update(
                current.type
            )
        )


        # ----------------------------------------------
        # 카테고리 수정
        # ----------------------------------------------

        new_category = (
            choose_category_for_update(
                category_repository,
                current.category,
            )
        )


        # ----------------------------------------------
        # 금액 수정
        # ----------------------------------------------

        amount_text = input(
            f"새 금액 [{current.amount}]: "
        ).strip()

        try:

            new_amount = (
                int(amount_text)
                if amount_text
                else None
            )

        except ValueError:

            print(
                "[수정 오류] 금액은 숫자로 입력해야 합니다."
            )

            raise SystemExit(1)


        # ----------------------------------------------
        # 메모 수정
        # ----------------------------------------------

        memo_text = input(
            f"새 메모 [{current.memo}]: "
        )

        new_memo = (
            memo_text
            if memo_text != ""
            else None
        )


        # ----------------------------------------------
        # 태그 수정
        # ----------------------------------------------

        tags_text = input(
            "새 태그(쉼표 구분 / Enter=기존 유지): "
        ).strip()

        if tags_text:

            new_tags = [
                tag.strip()
                for tag in tags_text.split(",")
                if tag.strip()
            ]

        else:

            new_tags = None


        # ----------------------------------------------
        # Service에 수정 요청
        # ----------------------------------------------

        try:

            updated = (
                transaction_service.update_transaction(
                    transaction_id=args.id,
                    transaction_type=new_type,
                    date=new_date,
                    amount=new_amount,
                    category=new_category,
                    memo=new_memo,
                    tags=new_tags,
                )
            )

            print("\n[수정 완료]")

            print(
                f"{updated.date} | "
                f"{updated.type} | "
                f"{updated.category} | "
                f"{updated.amount:,}원 | "
                f"{updated.memo}"
            )

        except ValueError as error:

            print(
                f"[수정 오류] {error}"
            )

            raise SystemExit(1)

        return


    # ======================================================
    # [17] delete 명령어 실행
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
    # [18] category 명령어 실행
    # ======================================================

    if args.command == "category":

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
    # [19] 명령어가 없으면 도움말 출력
    # ======================================================

    parser.print_help()