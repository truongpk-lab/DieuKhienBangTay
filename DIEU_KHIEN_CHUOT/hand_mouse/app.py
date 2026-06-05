"""Compatibility wrapper for ``backend.hand_runtime.app``."""

from backend.hand_runtime.app import HandMouseApp, build_parser, main

__all__ = ["HandMouseApp", "build_parser", "main"]


if __name__ == "__main__":
    main()
