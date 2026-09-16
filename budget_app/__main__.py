from budget_app.cli import main
from budget_app.decorators import safe_entry


# ==========================================================
# [1] python -m budget_app 실행 시작점
# ==========================================================
# 터미널에서
#
# python -m budget_app
#
# 를 실행하면 cli.py의 main() 함수를 실행함
# ==========================================================

if __name__ == "__main__":
    safe_main = safe_entry(main)
    safe_main()