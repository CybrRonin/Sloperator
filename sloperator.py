import sys
from pathlib import Path

from sloperator.runner import check_source, run_program

USAGE = "usage: uv run sloperator.py [--check] <file.slop>"


def main(argv: list[str]) -> int:
    args = argv[1:]
    check = "--check" in args
    if check:
        args = [arg for arg in args if arg != "--check"]

    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2

    path = Path(args[0])
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"could not read '{path}': {error.strerror}", file=sys.stderr)
        return 2

    error = check_source(source) if check else run_program(source, sys.stdout)
    if error is not None:
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
