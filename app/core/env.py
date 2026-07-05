import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_EXAMPLE_FILE = ROOT_DIR / ".env.example"
ENV_FILE = ROOT_DIR / ".env"


def ensure_env_file(verbose: bool = False) -> bool:
    if ENV_FILE.exists():
        if verbose:
            print(f"Файл {ENV_FILE.name} уже существует, пропускаю.")
        return False

    if not ENV_EXAMPLE_FILE.exists():
        if verbose:
            print(f"Файл {ENV_EXAMPLE_FILE.name} не найден.")
        return False

    shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)
    if verbose:
        print(f"Создан {ENV_FILE.name} на основе {ENV_EXAMPLE_FILE.name}.")
    return True
