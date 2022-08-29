from enum import Enum, IntEnum
import carb.settings

FONT_OFFSET_Y = carb.settings.get_settings().get("/app/font/offset_y") or 0


class FontSize:
    Normal = 14  # Default (In VIEW, 18 pixels in real, configed by /app/font/size)
    Large = 16  # real size = round(18*16/14) = 21
    XLarge = 18  # real size = round(18*18/14) = 23
    XXLarge = 20  # real size = round(18*20/14) = 26
    XXXLarge = 22  # real size = round(18*22/14) = 28
    Small = 12  # real size = round(18*12/14) = 15
    XSmall = 10  # real size = round(18*10/14) = 13
    XXSmall = 8  # real size = round(18*8/14) = 10
    XXXSmall = 6  # real size = round(18*6/14) = 8


class MouseKey(IntEnum):
    NONE = -1
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2


class COLORS:
    CLR_0 = 0xFF080808
    CLR_1 = 0xFF181818
    CLR_2 = 0xFF282828
    CLR_3 = 0xFF383838
    CLR_4 = 0xFF484848
    CLR_5 = 0xFF585858
    CLR_6 = 0xFF686868
    CLR_7 = 0xFF787878
    CLR_8 = 0xFF888888
    CLR_9 = 0xFF989898
    CLR_A = 0xFFA8A8A8
    CLR_B = 0xFFB8B8B8
    CLR_C = 0xFFCCCCCC
    CLR_D = 0xFFE0E0E0
    CLR_E = 0xFFF4F4F4

    LIGHRT_GARY = 0xFF808080
    GRAY = 0xFF606060
    DARK_GRAY = 0xFF404040
    DARK_DARK = 0xFF202020

    TRANSPARENT = 0x0000000

    # Color for buttons selected/activated state in NvidiaLight.
    L_SELECTED = 0xFFCFCCBF

    # Color for buttons selected/activated state in NvidiaDark.
    D_SELECTED = 0xFF4F383F

    BLACK = 0xFF000000
    WHITE = 0xFFFFFFFF

    TEXT_LIGHT = CLR_D
    TEXT_DISABLED_LIGHT = 0xFFA0A0A0
    TEXT_DARK = CLR_C
    TEXT_DISABLED_DARK = 0xFF8B8A8A
    TEXT_SELECTED = 0xFFC5911A

    WIDGET_BACKGROUND_LIGHT = 0xFF535354
    WIDGET_BACKGROUND_DARK = 0xFF23211F

    BUTTON_BACKGROUND_LIGHT = 0xFFD6D6D6

    LINE_SEPARATOR = 0xFFACACAC
    LINE_SEPARATOR_THICK = 0xFF666666


class LightColors:
    Background = COLORS.WIDGET_BACKGROUND_LIGHT
    BackgroundSelected = COLORS.CLR_4
    BackgroundHovered = COLORS.CLR_4
    Text = COLORS.CLR_D
    TextDisabled = COLORS.TEXT_DISABLED_LIGHT
    TextSelected = COLORS.TEXT_SELECTED
    Button = COLORS.BUTTON_BACKGROUND_LIGHT
    ButtonHovered = COLORS.CLR_B
    ButtonPressed = COLORS.CLR_A
    ButtonSelected = 0xFFCFCCBF
    WindowBackground = COLORS.CLR_D


class DarkColors:
    Background = COLORS.WIDGET_BACKGROUND_DARK
    BackgroundSelected = 0xFF6E6E6E
    BackgroundHovered = 0xFF6E6E6E
    Text = COLORS.CLR_C
    TextDisabled = COLORS.TEXT_DISABLED_DARK
    TextSelected = COLORS.TEXT_SELECTED
    Button = COLORS.WIDGET_BACKGROUND_DARK
    ButtonHovered = 0xFF9E9E9E
    ButtonPressed = 0xFF787569
    ButtonSelected = 0xFF4F383F
    WindowBackground = 0xFF454545
