#!/usr/bin/env python
"""ELITEFX GLASS BOX dashboard — Django manage entrypoint (read-only monitoring)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elitefx_dash.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
