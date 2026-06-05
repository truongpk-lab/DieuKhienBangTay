from actions import DryRunMouseController as ExportedDryRunMouseController
from actions import MouseController as ExportedMouseController
from actions.mouse_controller import DryRunMouseController, MouseController
from backend.hand_runtime.mouse import (
    DryRunMouseController as CanonicalDryRunMouseController,
)
from backend.hand_runtime.mouse import MouseController as CanonicalMouseController


def test_actions_mouse_controller_uses_backend_hand_runtime_canonical_logic():
    assert MouseController is CanonicalMouseController
    assert DryRunMouseController is CanonicalDryRunMouseController


def test_actions_package_exports_canonical_mouse_controllers():
    assert ExportedMouseController is CanonicalMouseController
    assert ExportedDryRunMouseController is CanonicalDryRunMouseController
