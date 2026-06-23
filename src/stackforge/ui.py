from colorama import Fore, Style, init

init(autoreset=True)

__all__ = [
    "BANNER", "banner", "section", "step", "file_created", "success",
    "warn", "error", "info", "prompt", "menu_item", "done", "muted",
    "Fore", "Style",
]

BANNER = r"""
  _____ _             _    ______
 / ____| |           | |  |  ____|
| (___ | |_ __ _  ___| | _| |__ ___  _ __ __ _  ___
 \___ \| __/ _` |/ __| |/ /  __/ _ \| '__/ _` |/ _ \
 ____) | || (_| | (__|   <| | | (_) | | | (_| |  __/
|_____/ \__\__,_|\___|_|\_\_|  \___/|_|  \__, |\___|
                                           __/ |
                                          |___/"""


def banner(subtitle: str, version: str = "") -> None:
    print(f"{Style.BRIGHT}{Fore.CYAN}{BANNER}{Style.RESET_ALL}")
    print(f"  {Style.BRIGHT}{Fore.WHITE}{subtitle}{Style.RESET_ALL}", end="")
    if version:
        print(f"  {Fore.LIGHTBLACK_EX}v{version}{Style.RESET_ALL}")
    else:
        print()


def section(title: str) -> None:
    print(f"\n  {Style.BRIGHT}{Fore.CYAN}> {title}{Style.RESET_ALL}")


def step(label: str) -> None:
    print(f"  {Fore.BLUE}|{Style.RESET_ALL} {label}")


def file_created(path: str) -> None:
    print(f"    {Fore.GREEN}+{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{path}{Style.RESET_ALL}")


def success(message: str) -> None:
    print(f"  {Fore.GREEN}+{Style.RESET_ALL} {message}")


def warn(message: str) -> None:
    print(f"  {Fore.YELLOW}!{Style.RESET_ALL}  {message}")


def error(message: str) -> None:
    print(f"  {Fore.RED}x{Style.RESET_ALL}  {message}")


def info(message: str) -> None:
    print(f"  {Fore.CYAN}{message}{Style.RESET_ALL}")


def prompt(label: str) -> str:
    return input(f"  {Style.BRIGHT}{Fore.CYAN}{label}{Style.RESET_ALL} ").strip()


def menu_item(key: str, label: str, *, style: str = Fore.GREEN) -> None:
    print(f"    {style}{key:<10}{Style.RESET_ALL} {label}")


def done() -> None:
    print(f"\n  {Style.BRIGHT}{Fore.GREEN}+ Scaffold complete.{Style.RESET_ALL}")


def muted(message: str) -> None:
    print(f"  {Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}")
