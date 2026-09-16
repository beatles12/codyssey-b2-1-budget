from budget_app.cli import run_cli
from budget_app.decorators import safe_entry


# CLI를 시작하면서 공통 오류 처리를 한 번 적용한다.
@safe_entry
def main() -> None:
    run_cli()


if __name__ == '__main__':
    main()
