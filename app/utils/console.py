from typing import Any


class Colors:
    """Цвета для терминала"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'


class Console:
    """Вывод в консоль"""

    @staticmethod
    def success(text: str):
        print(f"{Colors.GREEN} {text}{Colors.ENDC}")

    @staticmethod
    def error(text: str):
        print(f"{Colors.RED} {text}{Colors.ENDC}")

    @staticmethod
    def warning(text: str):
        print(f"{Colors.YELLOW} {text}{Colors.ENDC}")

    @staticmethod
    def info(text: str):
        print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

    @staticmethod
    def header(text: str, char: str = "=", length: int = 60):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{char * length}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}"
              f"{text.center(length)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{char * length}{Colors.ENDC}\n")

    @staticmethod
    def sub_header(text: str):
        print(f"\n{Colors.BOLD}┌─ {text}{Colors.ENDC}")

    @staticmethod
    def print_key_value(key: str, value: Any, key_width: int = 20):
        """Печатает пару ключ-значение"""
        print(f"  {Colors.BOLD}{key.ljust(key_width)}:{Colors.ENDC} {value}")
