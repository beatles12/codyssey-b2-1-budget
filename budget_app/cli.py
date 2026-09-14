import argparse
from datetime import datetime

from budget_app.repository import (
    BudgetRepository,
    CategoryRepository,
    TransactionRepository,
)
from budget_app.service import (
    BudgetService,
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
# [6] CLI 시작
# ==========================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description="나만의 용돈 기입장 프로그램"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )


    # ======================================================
    # [7] add
    # ======================================================

    subparsers.add_parser(
        "add",
        help="새 거래 추가"
    )


    # ======================================================
    # [8] list
    # ======================================================

    list_parser = subparsers.add_parser(
        "list",
        help="저장된 거래 목록 조회"
    )

    list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="출력할 최대 거래 수"
    )


    # ======================================================
    # [9] search
    # ======================================================

    search_parser = subparsers.add_parser(
        "search",
        help="조건으로 거래 검색"
    )

    search_parser.add_argument(
        "--from",
        dest="date_from"
    )

    search_parser.add_argument(
        "--to",
        dest="date_to"
    )

    search_parser.add_argument(
        "--category"
    )

    search_parser.add_argument(
        "--type",
        dest="transaction_type"
    )

    search_parser.add_argument(
        "--q"
    )

    search_parser.add_argument(
        "--tag"
    )


    # ======================================================
    # [10] summary
    # ======================================================

    summary_parser = subparsers.add_parser(
        "summary",
        help="월별 요약"
    )

    summary_parser.add_argument(
        "--month",
        required=True
    )

    summary_parser.add_argument(
        "--top",
        type=int,
        default=3
    )


    # ======================================================
    # [11] update
    # ======================================================

    update_parser = subparsers.add_parser(
        "update",
        help="거래 수정"
    )

    update_parser.add_argument(
        "--id",
        required=True
    )


    # ======================================================
    # [12] delete
    # ======================================================

    delete_parser = subparsers.add_parser(
        "delete",
        help="거래 삭제"
    )

    delete_parser.add_argument(
        "--id",
        required=True
    )


    # ======================================================
    # [13] category
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
        "list"
    )

    category_subparsers.add_parser(
        "add"
    )

    category_subparsers.add_parser(
        "remove"
    )


    # ======================================================
    # [14] budget
    # ======================================================
    # 예:
    # python -m budget_app budget set --month 2026-09 --amount 600000
    # python -m budget_app budget get --month 2026-09
    # ======================================================

    budget_parser = subparsers.add_parser(
        "budget",
        help="월별 예산 관리"
    )

    budget_subparsers = (
        budget_parser.add_subparsers(
            dest="budget_command"
        )
    )

    budget_set_parser = (
        budget_subparsers.add_parser(
            "set",
            help="월별 예산 저장"
        )
    )

    budget_set_parser.add_argument(
        "--month",
        required=True
    )

    budget_set_parser.add_argument(
        "--amount",
        type=int,
        required=True
    )

    budget_get_parser = (
        budget_subparsers.add_parser(
            "get",
            help="월별 예산 조회"
        )
    )

    budget_get_parser.add_argument(
        "--month",
        required=True
    )


    # ======================================================
    # [15] 명령어 읽기
    # ======================================================

    args = parser.parse_args()


    # ======================================================
    # [16] Repository / Service 준비
    # ======================================================

    transaction_repository = (
        TransactionRepository()
    )

    category_repository = (
        CategoryRepository()
    )

    budget_repository = (
        BudgetRepository()
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

    budget_service = (
        BudgetService(
            budget_repository
        )
    )


    # ======================================================
    # [17] add 실행
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

            amount = int(
                input(
                    "금액(양수): "
                ).strip()
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
                f"[저장 완료] id={transaction.id}"
            )

        except ValueError as error:

            print(
                f"[입력 오류] {error}"
            )

            raise SystemExit(1)

        return


    # ======================================================
    # [18] list 실행
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
    # [19] search 실행
    # ======================================================

    if args.command == "search":

        found = False

        try:

            transactions = (
                transaction_service.search_transactions(
                    date_from=args.date_from,
                    date_to=args.date_to,
                    category=args.category,
                    transaction_type=args.transaction_type,
                    query=args.q,
                    tag=args.tag,
                )
            )

            for number, transaction in enumerate(
                transactions,
                start=1
            ):

                found = True

                print(
                    f"\n[{number}] "
                    f"{transaction.date} | "
                    f"{transaction.type} | "
                    f"{transaction.category} | "
                    f"{transaction.amount:,}원 | "
                    f"{transaction.memo}"
                )

                print(
                    f"    tags: {', '.join(transaction.tags)}"
                )

                print(
                    f"    id: {transaction.id}"
                )

        except ValueError as error:

            print(
                f"[검색 오류] {error}"
            )

            raise SystemExit(1)

        if not found:
            print(
                "검색 결과가 없습니다."
            )

        return


    # ======================================================
    # [20] summary 실행
    # ======================================================
    # 월별 수입 / 지출 / 잔액을 보여주고
    # 예산이 설정되어 있으면
    # 예산 사용률과 초과 여부도 함께 보여줌
    # ======================================================

    if args.command == "summary":

        try:

            summary = (
                transaction_service.summarize_month(
                    args.month,
                    args.top,
                )
            )

            budget_status = (
                budget_service.get_budget_status(
                    args.month,
                    summary["total_expense"],
                )
            )

        except ValueError as error:

            print(
                f"[요약 오류] {error}"
            )

            raise SystemExit(1)


        # 거래가 하나도 없는 경우
        if summary["transaction_count"] == 0:

            print(
                f"{args.month}: 데이터 없음"
            )

            return
        

        # ----------------------------------------------
        # 월별 거래 요약
        # ----------------------------------------------

        print(
            f"\n[월별 요약] {summary['month']}"
        )

        print(
            f"거래 건수: "
            f"{summary['transaction_count']}건"
        )

        print(
            f"총 수입: "
            f"{summary['total_income']:,}원"
        )

        print(
            f"총 지출: "
            f"{summary['total_expense']:,}원"
        )

        print(
            f"잔액: "
            f"{summary['balance']:,}원"
        )


        # ----------------------------------------------
        # 지출 카테고리 TOP N
        # ----------------------------------------------

        print(
            f"\n[지출 카테고리 TOP {args.top}]"
        )

        if not summary["top_categories"]:

            print(
                "지출 데이터가 없습니다."
            )

        else:

            for rank, (
                category,
                amount,
            ) in enumerate(
                summary["top_categories"],
                start=1
            ):

                print(
                    f"{rank}. "
                    f"{category}: "
                    f"{amount:,}원"
                )


        # ----------------------------------------------
        # 예산 현황
        # ----------------------------------------------

        if budget_status is None:

            print(
                "\n[예산 현황]"
            )

            print(
                "설정된 예산이 없습니다."
            )

        else:

            print(
                "\n[예산 현황]"
            )

            print(
                f"월 예산: "
                f"{budget_status['budget']:,}원"
            )

            print(
                f"사용액: "
                f"{budget_status['spent']:,}원"
            )

            print(
                f"예산 사용률: "
                f"{budget_status['usage_rate']:.1f}%"
            )


            if budget_status["exceeded"]:

                exceeded_amount = abs(
                    budget_status["remaining"]
                )

                print(
                    f"예산 초과: "
                    f"{exceeded_amount:,}원"
                )

            else:

                print(
                    f"남은 예산: "
                    f"{budget_status['remaining']:,}원"
                )

        return       


    # ======================================================
    # [21] update 실행
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
        print(f"날짜: {current.date}")
        print(f"종류: {current.type}")
        print(f"카테고리: {current.category}")
        print(f"금액: {current.amount:,}원")
        print(f"메모: {current.memo}")
        print(f"태그: {', '.join(current.tags)}")

        date_text = input(
            f"새 날짜 [{current.date}]: "
        ).strip()

        new_date = (
            normalize_date_input(date_text)
            if date_text
            else None
        )

        new_type = (
            choose_transaction_type_for_update(
                current.type
            )
        )

        new_category = (
            choose_category_for_update(
                category_repository,
                current.category,
            )
        )

        amount_text = input(
            f"새 금액 [{current.amount}]: "
        ).strip()

        new_amount = (
            int(amount_text)
            if amount_text
            else None
        )

        memo_text = input(
            f"새 메모 [{current.memo}]: "
        )

        new_memo = (
            memo_text
            if memo_text != ""
            else None
        )

        tags_text = input(
            "새 태그(쉼표 구분 / Enter=기존 유지): "
        ).strip()

        new_tags = (
            [
                tag.strip()
                for tag in tags_text.split(",")
                if tag.strip()
            ]
            if tags_text
            else None
        )

        try:

            updated = (
                transaction_service.update_transaction(
                    args.id,
                    new_type,
                    new_date,
                    new_amount,
                    new_category,
                    new_memo,
                    new_tags,
                )
            )

            print(
                f"[수정 완료] "
                f"{updated.amount:,}원"
            )

        except ValueError as error:

            print(
                f"[수정 오류] {error}"
            )

            raise SystemExit(1)

        return


    # ======================================================
    # [22] delete 실행
    # ======================================================

    if args.command == "delete":

        answer = input(
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
    # [23] category 실행
    # ======================================================

    if args.command == "category":

        if args.category_command == "list":

            for number, category in enumerate(
                category_service.list_categories(),
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
    # [24] budget 실행
    # ======================================================

    if args.command == "budget":

        # ----------------------------------------------
        # budget set
        # ----------------------------------------------

        if args.budget_command == "set":

            try:

                budget_service.set_budget(
                    args.month,
                    args.amount,
                )

                print(
                    f"[예산 저장 완료] "
                    f"{args.month} = "
                    f"{args.amount:,}원"
                )

            except ValueError as error:

                print(
                    f"[예산 오류] {error}"
                )

                raise SystemExit(1)

            return


        # ----------------------------------------------
        # budget get
        # ----------------------------------------------

        if args.budget_command == "get":

            try:

                amount = budget_service.get_budget(
                    args.month
                )

            except ValueError as error:

                print(
                    f"[예산 오류] {error}"
                )

                raise SystemExit(1)

            if amount is None:

                print(
                    f"{args.month}: 설정된 예산 없음"
                )

            else:

                print(
                    f"{args.month} 예산: "
                    f"{amount:,}원"
                )

            return

        budget_parser.print_help()
        return


    # ======================================================
    # [25] 명령어가 없으면 도움말
    # ======================================================

    parser.print_help()