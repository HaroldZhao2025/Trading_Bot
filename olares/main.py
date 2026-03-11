import argparse

from .arb_scan import run as arb_run
from .dex_runner import main as dex_main
from .validate_dex import main as validate_dex_main


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("arb-scan")
    sub.add_parser("dex-scan")
    sub.add_parser("hl-paper")
    sub.add_parser("validate-dex")

    args, rest = p.parse_known_args()

    if args.cmd == "arb-scan":
        arb_run()
    elif args.cmd in {"dex-scan", "hl-paper"}:
        import sys
        sys.argv = [sys.argv[0], args.cmd] + rest
        dex_main()
    elif args.cmd == "validate-dex":
        import sys
        sys.argv = [sys.argv[0]] + rest
        validate_dex_main()


if __name__ == "__main__":
    main()