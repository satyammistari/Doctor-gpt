from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from services.background_worker import BackgroundWorker
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.animation import Animation
from widgets.custom_widgets import ChatBubble
from services.background_worker import BackgroundWorker
from services.chat_responder import get_random_reply
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from widgets.custom_widgets import ChatBubble
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import NumericProperty

class HomeScreen(Screen):
    worker = None
    rect_alpha = NumericProperty(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        pass

    def add_message_bubble(self, text: str, is_user: bool):
        wrapper = AnchorLayout(size_hint_y=None, height=dp(40)) 
        wrapper.anchor_x = 'right' if is_user else 'left'

        bubble = ChatBubble(text=text, is_user=is_user)
        wrapper.add_widget(bubble)
        self.ids.messages_box.add_widget(wrapper)

        def adjust_height(dt):
            wrapper.height = bubble.height
            Clock.schedule_once(lambda d: self.ids.scroll_box.scroll_to(wrapper), 0)

        Clock.schedule_once(adjust_height, 0)

    def on_message_sent(self, text):
        self.add_message_bubble(text=text, is_user = True)
        Clock.schedule_once(lambda dt: self._add_bot_reply(text), 0.6)

    def animate_bar_and_add_message(self, message):
        from kivy.animation import Animation

        textbar = self.ids.get("textbar")
        title = self.ids.get("doctor_title")
        if not textbar:
            return

        bottom_margin = dp(16)
        target_y = bottom_margin

        Animation.cancel_all(textbar)
        bar_anim = Animation(y=target_y, d=0.3, t="out_cubic")
        til_ani = Animation(y=-10, d = 0.3, t="out_cubic")

        def _on_done(animation, widget):
            self.add_message_bubble(message)
            Clock.schedule_once(lambda dt: self.scroll_messages_to_bottom(), 0)

        bar_anim.bind(on_complete=_on_done)
        til_ani.start(title)
        bar_anim.start(textbar)

    def _add_bot_reply(self, user_text: str):
        reply_text = get_random_reply(user_text)
        self.add_message_bubble(reply_text, is_user=False)


    def scroll_messages_to_bottom(self):

        scroll = self.ids.messages_scroll
