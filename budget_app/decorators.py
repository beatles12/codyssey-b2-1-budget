from typing import Callable, TypeVar

T = TypeVar('T')


# 진입점에서 사용자 오류를 안내하고 실패 코드로 종료한다.
def safe_entry(func: Callable[..., T]) -> Callable[..., T]:
    # 감싼 함수를 실행하고 예외를 공통 방식으로 처리한다.
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print('\n[중단] 사용자가 프로그램 실행을 중단했습니다.')
        except EOFError:
            print('\n[입력 오류] 입력이 예상보다 일찍 종료되었습니다.')
            print('[힌트] 다시 실행한 뒤 필요한 값을 입력해주세요.')
        except ValueError as error:
            print(f'[입력 오류] {error}')
            print('[힌트] 입력 형식과 값을 확인한 뒤 다시 실행해주세요.')
        except OSError as error:
            print(f'[파일 오류] {error}')
            print('[힌트] 파일 경로와 접근 권한을 확인해주세요.')
        raise SystemExit(1)
    return wrapper
