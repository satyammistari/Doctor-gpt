from kivy.uix.accordion import BooleanProperty
from kivy.uix.accordion import Animation
from kivy.uix.button import Button
from kivy.properties import StringProperty

from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.app import App
class FancyButton(Button):
    subtitle = StringProperty("")

from kivy.properties import NumericProperty, ObjectProperty
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.metrics import dp
import os

# path = ""
class TextBar(Widget):
    clamped_width = NumericProperty(0)
    min_width = NumericProperty(400)
    max_width = NumericProperty(1400)
    selected_image_path = StringProperty("")   
    selected_image_name = StringProperty("")  
    attachment_width = NumericProperty(0)
    message_sent = ObjectProperty(None, allownone=True)
    image_selected = ObjectProperty(None, allownone=True)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.on_window_resize)
        self._file_popup = None
        self.on_window_resize(Window, Window.size)

    def on_window_resize(self, window, size):
        w, _ = size
        if w < self.min_width:
            w_eff = self.min_width
        elif w > self.max_width:
            w_eff = self.max_width
        else:
            w_eff = w
        self.clamped_width = w_eff

    def on_request_image(self, *args):
        pass

    def on_send_pressed(self):
        self.dispatch('on_request_image') 
    
    class ImageChip(BoxLayout):
        text = StringProperty("")
    
    def open_file_chooser(self):
        if self._file_popup and self._file_popup.parent:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif'],
                                      path=os.path.expanduser("C:/Users/Vedant/Desktop/archive"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        select_btn = Button(text="Select", size_hint_x=None, width=dp(100))
        cancel_btn = Button(text="Cancel", size_hint_x=None, width=dp(100))

        btn_row.add_widget(Label())  # spacer
        btn_row.add_widget(select_btn)
        btn_row.add_widget(cancel_btn)

        content.add_widget(chooser)
        content.add_widget(btn_row)

        popup = Popup(title="Select an image", content=content,
                      size_hint=(0.9, 0.9), auto_dismiss=False)
        self._file_popup = popup

        def on_select(instance):
            selection = chooser.selection
            if selection:
                self._apply_selected_file(selection[0])
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=on_cancel)

        popup.open()

    def _apply_selected_file(self, filepath):
        if not filepath:
            return
        self.selected_image_path = filepath
        self.selected_image_name = os.path.basename(filepath)
        App.get_running_app().selected_image_path = self.selected_image_path

    def clear_selection(self):
        self.selected_image_path = ""
        self.selected_image_name = ""

    def move_to_bottom(self, on_complete=None):
        bottom_margin = dp(16)
        target_y = bottom_margin
        anim = Animation(y=target_y, d=0.3, t="out_cubic")
        if on_complete:
            anim.bind(on_complete=lambda *args: on_complete())
        anim.start(self)

    def on_send_pressed(self):
        msg = self.ids.message_input.text.strip()
        if not msg:
            return

        self.ids.message_input.text = ""

        def after_anim():
            if self.message_sent:
                self.message_sent(msg)

        self.move_to_bottom(on_complete=after_anim)

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp

class ChatBubble(BoxLayout):
    text = StringProperty("")
    is_user = BooleanProperty(False)  

    max_width_frac = NumericProperty(0.95)
    horiz_padding  = NumericProperty(dp(18))
    min_width      = NumericProperty(dp(300))

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, padding=dp(8), **kwargs)
        Clock.schedule_once(self._setup, 0)

    def _setup(self, *a):
        self.msg_label = self.ids.get("msg_label", None)
        if self.msg_label:
            self.msg_label.bind(texture_size=self._update_size)
        if self.parent:
            self.parent.bind(width=self._update_size)
        self._update_size()

    def _update_size(self, *largs):
        if not hasattr(self, "msg_label") or self.msg_label is None:
            return

        label_w = self.msg_label.texture_size[0]

        parent_w = self.parent.width if (self.parent is not None) else 300
        max_allowed = parent_w * self.max_width_frac

        desired = label_w + self.horiz_padding
        final_w = max(self.min_width, min(desired, max_allowed))

        self.width = final_w
        self.height = self.msg_label.texture_size[1] + self.padding[1] * 2

        if self.parent and hasattr(self.parent, "height"):
            try:
                self.parent.height = self.height
            except Exception:
                pass
