from .mouse_controller import MouseController


class MouseControlAdapter:
    """Thin compatibility layer over the canonical hand-mouse controller."""

    def __init__(self, controller=None):
        self.controller = controller if controller is not None else MouseController()

    @property
    def enabled(self):
        return self.controller.enabled

    @property
    def screen_w(self):
        return self.controller.screen_w

    @property
    def screen_h(self):
        return self.controller.screen_h

    def move(self, x, y):
        return self.controller.move_to(x, y)

    def click(self, button="left", clicks=1):
        return self.controller.click(button=button, clicks=clicks)

    def left_click(self, clicks=1):
        return self.controller.click(button="left", clicks=clicks)

    def right_click(self, clicks=1):
        return self.controller.click(button="right", clicks=clicks)

    def scroll(self, amount):
        return self.controller.scroll(amount)

    def mouse_down(self):
        return self.controller.mouse_down()

    def mouse_up(self):
        return self.controller.mouse_up()

    def drag_start(self):
        return self.controller.mouse_down()

    def drag_move(self, x, y):
        return self.controller.move_to(x, y)

    def drag_release(self):
        return self.controller.mouse_up()
