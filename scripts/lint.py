import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "black", "."],
    [sys.executable, "-m", "flake8"],
    [sys.executable, "-m", "mypy", "app"],
]


def main() -> int:
    exit_code = 0
    for command in COMMANDS:
        print(f"\n$ {' '.join(command)}")
        result = subprocess.run(command)
        if result.returncode != 0:
            exit_code = result.returncode
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
