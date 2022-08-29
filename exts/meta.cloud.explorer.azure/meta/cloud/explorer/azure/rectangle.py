from omni import ui

from .constant import COLORS


# A rectangle that will block mouse events to deeper
class OpaqueRectangle(ui.Rectangle):
    def __init__(self, **kwargs):
        kwargs["opaque_for_mouse_events"] = True
        kwargs["mouse_pressed_fn"] = lambda *_: self._dummy()
        super().__init__(**kwargs)

    def _dummy(self):
        pass


class ShortSeparator:
    def __init__(self, height):
        self._panel = ui.HStack(width=2, height=height)
        with self._panel:
            with ui.VStack(width=2, height=height, style={"Line": {"color": COLORS.LIGHRT_GARY, "border_width": 1}}):
                ui.Spacer(height=2)
                ui.Line(width=1, alignment=ui.Alignment.LEFT)
                ui.Line(width=1, alignment=ui.Alignment.LEFT)
                ui.Spacer(height=2)


class DashRectangle:
    def __init__(self, width, height, padding_x=2, padding_y=2, w_step=10, h_step=10):
        w_num = int((width - 2 * padding_x - 2) / w_step)
        h_num = int((height - 2 * padding_y) / h_step)
        with ui.ZStack():
            with ui.VStack(style={"Line": {"color": COLORS.LIGHRT_GARY, "border_width": 1}}):
                ui.Spacer(height=padding_y)
                self._build_horizontal_line(w_num, padding_x)
                ui.Spacer(height=height - 2 * padding_y - 2)
                self._build_horizontal_line(w_num, padding_x)
                ui.Spacer(height=padding_y)
            with ui.HStack(height=height):
                ui.Spacer(width=padding_x)
                self._build_vertical_line(height, h_step, h_num, padding_y)
                ui.Spacer()
                self._build_vertical_line(height, h_step, h_num, padding_y)
                ui.Spacer(width=padding_x - 2)

    def _build_horizontal_line(self, w_num, padding_x):
        with ui.HStack():
            ui.Spacer(width=padding_x)
            for _ in range(w_num):
                ui.Line(width=6, height=1)
                ui.Spacer()
            ui.Line(height=1)
            ui.Spacer(width=padding_x)

    def _build_vertical_line(self, height, h_step, h_num, padding_y):
        with ui.VStack(width=2, height=height):
            ui.Spacer(height=padding_y)
            for _ in range(h_num):
                ShortSeparator(h_step)
