import argparse
from datetime import datetime
from pathlib import Path

from budget_app.csv_service import CsvService
from budget_app.repository import BudgetRepository, CategoryRepository, TransactionRepository
from budget_app.service import BudgetService, CategoryService, TransactionService

# 빈 날짜와 숫자 날짜를 ISO 날짜로 바꾼다.
def normalize_date_input(date_text: str) -> str:
    if not date_text:
        return datetime.now().strftime('%Y-%m-%d')
    if len(date_text) == 8 and date_text.isdigit():
        return f'{date_text[:4]}-{date_text[4:6]}-{date_text[6:]}'
    return date_text

# 금액 문자열을 정수로 바꾸고 잘못된 입력을 안내한다.
def parse_amount(amount_text: str) -> int:
    if not amount_text.lstrip('-').isdecimal():
        raise ValueError('금액은 숫자로 입력해야 합니다. 예: 15000')
    return int(amount_text)

# 거래 종류를 번호로 선택받는다.
def choose_transaction_type() -> str:
    print('\n[거래 종류 선택]')
    print('1. income  (수입)')
    print('2. expense (지출)')
    while True:
        choice = input('번호 선택: ').strip()
        if choice == '1':
            return 'income'
        if choice == '2':
            return 'expense'
        print('1 또는 2를 입력해주세요.')

# 기존 값 유지를 포함해 거래 종류를 선택받는다.
def choose_transaction_type_for_update(current_type: str) -> str | None:
    print(f'\n현재 거래 종류: {current_type}')
    print('1. income  (수입)')
    print('2. expense (지출)')
    print('Enter. 기존 값 유지')
    while True:
        choice = input('번호 선택: ').strip()
        if choice == '':
            return None
        if choice == '1':
            return 'income'
        if choice == '2':
            return 'expense'
        print('1, 2 또는 Enter를 입력해주세요.')

# 등록된 카테고리를 번호로 선택받는다.
def choose_category(category_repository: CategoryRepository) -> str:
    categories = list(category_repository.iter_categories())
    print('\n[카테고리 선택]')
    for number, category in enumerate(categories, start=1):
        print(f'{number}. {category}')
    while True:
        choice = input('번호 선택: ').strip()
        if choice.isdecimal():
            number = int(choice)
            if 1 <= number <= len(categories):
                return categories[number - 1]
        print('목록에 있는 번호를 입력해주세요.')

# 기존 값 유지를 포함해 카테고리를 선택받는다.
def choose_category_for_update(category_repository: CategoryRepository, current_category: str) -> str | None:
    categories = list(category_repository.iter_categories())
    print(f'\n현재 카테고리: {current_category}')
    for number, category in enumerate(categories, start=1):
        print(f'{number}. {category}')
    print('Enter. 기존 값 유지')
    while True:
        choice = input('번호 선택: ').strip()
        if choice == '':
            return None
        if choice.isdecimal():
            number = int(choice)
            if 1 <= number <= len(categories):
                return categories[number - 1]
        print('목록 번호 또는 Enter를 입력해주세요.')

# 명령어와 옵션의 도움말 구조를 만든다.
def build_parser() -> tuple[argparse.ArgumentParser, argparse.ArgumentParser, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(description='나만의 용돈 기입장 프로그램')
    parser.add_argument('--data-dir', default='data', help='데이터 저장 폴더 (기본값: data)')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('add', help='새 거래 추가')
    list_parser = subparsers.add_parser('list', help='저장된 거래 목록 조회')
    list_parser.add_argument('--limit', type=int, default=20, help='출력할 최대 거래 수')
    search_parser = subparsers.add_parser('search', help='조건으로 거래 검색')
    search_parser.add_argument('--from', dest='date_from')
    search_parser.add_argument('--to', dest='date_to')
    search_parser.add_argument('--category')
    search_parser.add_argument('--type', dest='transaction_type')
    search_parser.add_argument('--q')
    search_parser.add_argument('--tag')
    summary_parser = subparsers.add_parser('summary', help='월별 요약')
    summary_parser.add_argument('--month', required=True)
    summary_parser.add_argument('--top', type=int, default=3)
    export_parser = subparsers.add_parser('export', help='거래를 CSV 파일로 내보내기')
    export_parser.add_argument('--out', required=True, help='저장할 CSV 파일 경로')
    export_parser.add_argument('--month', help='내보낼 월 (YYYY-MM)')
    export_parser.add_argument('--from', dest='date_from', help='시작 날짜 (YYYY-MM-DD)')
    export_parser.add_argument('--to', dest='date_to', help='끝 날짜 (YYYY-MM-DD)')
    import_parser = subparsers.add_parser('import', help='CSV 파일의 거래 가져오기')
    import_parser.add_argument('--from', dest='from_path', required=True, help='가져올 CSV 파일 경로')
    update_parser = subparsers.add_parser('update', help='거래 수정')
    update_parser.add_argument('--id', required=True)
    delete_parser = subparsers.add_parser('delete', help='거래 삭제')
    delete_parser.add_argument('--id', required=True)
    category_parser = subparsers.add_parser('category', help='카테고리 관리')
    category_subparsers = category_parser.add_subparsers(dest='category_command')
    category_subparsers.add_parser('list')
    category_subparsers.add_parser('add')
    category_subparsers.add_parser('remove')
    budget_parser = subparsers.add_parser('budget', help='월별 예산 관리')
    budget_subparsers = budget_parser.add_subparsers(dest='budget_command')
    budget_set_parser = budget_subparsers.add_parser('set', help='월별 예산 저장')
    budget_set_parser.add_argument('--month', required=True)
    budget_set_parser.add_argument('--amount', type=int, required=True)
    budget_get_parser = budget_subparsers.add_parser('get', help='월별 예산 조회')
    budget_get_parser.add_argument('--month', required=True)
    return parser, category_parser, budget_parser

# 명령을 해석하고 해당 기능을 실행한다.
def run_cli() -> None:
    parser, category_parser, budget_parser = build_parser()
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    transaction_repository = TransactionRepository(str(data_dir / 'transactions.jsonl'))
    category_repository = CategoryRepository(str(data_dir / 'categories.jsonl'))
    budget_repository = BudgetRepository(str(data_dir / 'budgets.jsonl'))
    transaction_service = TransactionService(transaction_repository)
    category_service = CategoryService(category_repository, transaction_repository)
    budget_service = BudgetService(budget_repository)
    csv_service = CsvService(transaction_repository, category_repository)
    if args.command == 'add':
        
        while True:
            date_text = input('날짜(Enter=오늘 / 예: 2026-09-21): ').strip()
            date = normalize_date_input(date_text)

            error = transaction_service.get_date_validation_error(date)
            if error:
                print(f'[입력 오류] {error}')
                print('[힌트] 예: 2026-09-21')
                continue

            break

        transaction_type = choose_transaction_type()

        category = choose_category(category_repository)
        amount_text = input('금액(양수): ').strip()
        amount = parse_amount(amount_text)
        memo = input('메모(선택): ').strip()
        tags_text = input('태그(쉼표 구분 / 없으면 Enter): ').strip()
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        else:
            tags = []
        transaction = transaction_service.add_transaction(
            transaction_type=transaction_type, date=date, amount=amount,
            category=category, memo=memo, tags=tags,
        )
        print(f'[저장 완료] id={transaction.id}')
        return
    if args.command == 'list':
        transactions = transaction_service.list_transactions(limit=args.limit)
        if not transactions:
            print('저장된 거래가 없습니다.')
            return
        for number, transaction in enumerate(transactions, start=1):
            print(
                f'\n[{number}] {transaction.date} | {transaction.type} | '
                f'{transaction.category} | {transaction.amount:,}원 | {transaction.memo}'
            )
            print(f'    id: {transaction.id}')
        return
    if args.command == 'search':
        found = False
        transactions = transaction_service.search_transactions(
            date_from=args.date_from, date_to=args.date_to,
            category=args.category, transaction_type=args.transaction_type,
            query=args.q, tag=args.tag,
        )
        for number, transaction in enumerate(transactions, start=1):
            found = True
            print(
                f'\n[{number}] {transaction.date} | {transaction.type} | '
                f'{transaction.category} | {transaction.amount:,}원 | {transaction.memo}'
            )
            print(f"    tags: {', '.join(transaction.tags)}")
            print(f'    id: {transaction.id}')
        if not found:
            print('검색 결과가 없습니다.')
        return
    if args.command == 'summary':
        summary = transaction_service.summarize_month(args.month, args.top)
        budget_status = budget_service.get_budget_status(args.month, summary['total_expense'])
        if summary['transaction_count'] == 0:
            print(f'{args.month}: 데이터 없음')
            return
        print(f"\n[월별 요약] {summary['month']}")
        print(f"거래 건수: {summary['transaction_count']}건")
        print(f"총 수입: {summary['total_income']:,}원")
        print(f"총 지출: {summary['total_expense']:,}원")
        print(f"잔액: {summary['balance']:,}원")
        print(f'\n[지출 카테고리 TOP {args.top}]')
        if not summary['top_categories']:
            print('지출 데이터가 없습니다.')
        else:
            for rank, (category, amount) in enumerate(summary['top_categories'], start=1):
                print(f'{rank}. {category}: {amount:,}원')
        if budget_status is None:
            print('\n[예산 현황]')
            print('설정된 예산이 없습니다.')
        else:
            print('\n[예산 현황]')
            print(f"월 예산: {budget_status['budget']:,}원")
            print(f"사용액: {budget_status['spent']:,}원")
            print(f"예산 사용률: {budget_status['usage_rate']:.1f}%")
            if budget_status['exceeded']:
                exceeded_amount = abs(budget_status['remaining'])
                print(f'예산 초과: {exceeded_amount:,}원')
            else:
                print(f"남은 예산: {budget_status['remaining']:,}원")
        return
    if args.command == 'export':
        exported_count = csv_service.export_transactions(
            out_path=args.out, month=args.month,
            date_from=args.date_from, date_to=args.date_to,
        )
        print(f'[완료] {args.out} ({exported_count} records)')
        return
    if args.command == 'import':
        imported_count, skipped_count = csv_service.import_transactions(from_path=args.from_path)
        print(f'[완료] imported={imported_count}, skipped={skipped_count}')
        return
    if args.command == 'update':
        current = transaction_repository.find_by_id(args.id)
        if current is None:
            raise ValueError('해당 id의 거래를 찾을 수 없습니다.')
        print('\n[현재 거래]')
        print(f'날짜: {current.date}')
        print(f'종류: {current.type}')
        print(f'카테고리: {current.category}')
        print(f'금액: {current.amount:,}원')
        print(f'메모: {current.memo}')
        print(f"태그: {', '.join(current.tags)}")
        date_text = input(f'새 날짜 [{current.date}]: ').strip()
        new_date = normalize_date_input(date_text) if date_text else None
        new_type = choose_transaction_type_for_update(current.type)
        new_category = choose_category_for_update(category_repository, current.category)
        amount_text = input(f'새 금액 [{current.amount}]: ').strip()
        new_amount = parse_amount(amount_text) if amount_text else None
        memo_text = input(f'새 메모 [{current.memo}]: ')
        new_memo = memo_text if memo_text != '' else None
        tags_text = input('새 태그(쉼표 구분 / Enter=기존 유지): ').strip()
        new_tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else None
        updated = transaction_service.update_transaction(
            args.id, new_type, new_date, new_amount,
            new_category, new_memo, new_tags,
        )
        print(f'[수정 완료] {updated.amount:,}원')
        return
    if args.command == 'delete':
        answer = input('이 거래를 삭제할까요? (y/N): ').strip().lower()
        if answer != 'y':
            print('삭제를 취소했습니다.')
            return
        transaction_service.delete_transaction(args.id)
        print('[삭제 완료]')
        return
    if args.command == 'category':
        if args.category_command == 'list':
            for number, category in enumerate(category_service.list_categories(), start=1):
                print(f'{number}. {category}')
            return
        if args.category_command == 'add':
            category_name = input('추가할 카테고리 이름: ').strip()
            category_service.add_category(category_name)
            print(f'[추가 완료] {category_name}')
            return
        if args.category_command == 'remove':
            category_name = choose_category(category_repository)
            category_service.remove_category(category_name)
            print(f'[삭제 완료] {category_name}')
            return
        category_parser.print_help()
        return
    if args.command == 'budget':
        if args.budget_command == 'set':
            budget_service.set_budget(args.month, args.amount)
            print(f'[예산 저장 완료] {args.month} = {args.amount:,}원')
            return
        if args.budget_command == 'get':
            amount = budget_service.get_budget(args.month)
            if amount is None:
                print(f'{args.month}: 설정된 예산 없음')
            else:
                print(f'{args.month} 예산: {amount:,}원')
            return
        budget_parser.print_help()
        return
    parser.print_help()
