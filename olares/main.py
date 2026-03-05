import argparse
from .arb_scan import run as arb_run


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("arb-scan")
    args = p.parse_args()

    if args.cmd == "arb-scan":
        arb_run()


if __name__ == "__main__":
    main()