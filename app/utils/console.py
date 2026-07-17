class Colors:
    """Цвета для терминала"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class Console:
    """Минимальный вывод в консоль"""

    @staticmethod
    def success(text: str):
        print(f"{Colors.GREEN} {text}{Colors.ENDC}")

    @staticmethod
    def error(text: str):
        print(f"{Colors.RED} {text}{Colors.ENDC}")

    @staticmethod
    def warning(text: str):
        print(f"{Colors.YELLOW}  {text}{Colors.ENDC}")

    @staticmethod
    def info(text: str):
        print(f"{Colors.BLUE} {text}{Colors.ENDC}")

    @staticmethod
    def header(text: str):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
