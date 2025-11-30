from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.metrics import dp
from screens.home import HomeScreen
from widgets.custom_widgets import FancyButton  
from kivy.core.text import LabelBase
LabelBase.register(name="FA", fn_regular="assets/fasolid.ttf")
from kivy.app import App

class RootScreenManager(ScreenManager):
    pass

class MyApp(App):
    title = "My Kivy App"
    icon = "assets/logo.png"  
    selected_image_path = ""

    def build(self):
        Window.clearcolor = (41/255, 41/255, 41/255, 1)

        Builder.load_file("app.kv")
        sm = RootScreenManager()
        sm.add_widget(HomeScreen(name="home"))  
        return sm

if __name__ == "__main__":
    MyApp().run()