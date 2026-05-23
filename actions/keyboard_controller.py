"""Safe keyboard controller skeleton for mapped keyboard actions.

The Phase 12 mapper can route keyboard actions here, but this skeleton does
not send real key presses. A real backend can replace it in a later phase.
"""

from __future__ import annotations


class KeyboardController:
    """No-op keyboard controller with the future production API shape."""

    enabled = False

    def hotkey(self, *keys: str):
        return {"status": "skipped", "reason": "keyboard controller is not connected", "keys": keys}

    def press(self, key: str):
        return {"status": "skipped", "reason": "keyboard controller is not connected", "key": key}

    def release(self, key: str):
        return {"status": "skipped", "reason": "keyboard controller is not connected", "key": key}
