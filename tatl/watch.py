from watchfiles import run_process


def main() -> None:
    run_process("./tatl", target="poetry run tatl")
