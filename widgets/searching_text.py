from kivy.uix.textinput import TextInput
from kivy.lang import Builder


class SearchingText(TextInput):
    pass


kv = """
#:import Window kivy.core.window.Window


<SearchingText>:
    text: "Searching..."
    size_hint_y: None
    height: self.minimum_height
    font_name: "RobotoMono-Regular"
    font_size: str(min(Window.height/720*5, Window.width/720*5)) + 'sp'
    background_color: (0, 0, 0, 0)
    background_disabled_normal: ''
    disabled_foreground_color: app.text_color
    disabled: True
    halign: 'center'
"""

Builder.load_string(kv)
