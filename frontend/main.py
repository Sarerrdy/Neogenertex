import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from scan_menu import ScanMenu
from kivy.uix.boxlayout import BoxLayout
from print_menu import PrintMenu

video_path = os.path.join(os.path.dirname(__file__), 'resources', 'advert.mp4')


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.idle_event = None

    def on_touch_down(self, touch):
        self.handle_interaction()
        return super(MainScreen, self).on_touch_down(touch)

    def handle_interaction(self):
        # Pause the video replay
        video = self.ids.video
        video.state = 'stop'
        video.opacity = 0

        # Navigate to the MenuScreen
        self.manager.current = 'menu'


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.idle_event = None
        print("MenuScreen called")

    def on_touch_down(self, touch):
        print("On_Touch_down called")
        # Cancel the scheduled event
        if self.idle_event:
            self.idle_event.cancel()

        # Schedule a new event
        self.idle_event = Clock.schedule_once(self.resume_video, 10)

        # Call the superclass method
        super(MenuScreen, self).on_touch_down(touch)

    def on_enter(self):
        print("on_enter Scheduller video called")
        self.idle_event = Clock.schedule_once(self.resume_video, 10)

    def resume_video(self, dt):
        print("Resume video called")
        # Check if the MenuScreen is the current screen
        app = App.get_running_app()
        print("Before Confirmed current screen as main")
        # if self.manager.current == 'menu' and not app.print_popup and not app.print_message:
        if self.manager.current == 'menu':
            print("After Confirmed current screen as main")
            # Navigate back to the MainScreen
            self.manager.current = 'main'

            # Resume the video replay
            video = app.root.get_screen('main').ids.video
            video.state = 'play'
            video.opacity = 1


class KioskApp(App):
    def __init__(self, **kwargs):
        super(KioskApp, self).__init__(**kwargs)
        # self.menu_screen_active_alone = False
        # self.print_popup = None
        # self.print_menu = PrintMenu()

    def build(self):
        print("KioskApp build method called")
        return Builder.load_file('main.kv')
        

    def get_video_path(self):
        return video_path

    def print_function(self):
        # self.print_menu.print_function()
        self.root.current = 'print_menu'

    def scan_function(self):
        print("Scan function called")
        self.root.add_widget(ScanMenuScreen())
        self.root.current = 'scan_menu'

    def access_internet_function(self):
        print("Access internet function called")

    def stop_app(self, *args):
        print("stop_app method called")
        App.get_running_app().stop()
        print("Kivy app stopped")


class ScanMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(ScanMenuScreen, self).__init__(**kwargs)
        self.layout = ScanMenu()
        self.add_widget(self.layout)

    def scan_document(self):
        # Your scanning functionality here
        print('Scanning document...')


class PrintMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(PrintMenuScreen, self).__init__(**kwargs)
        # self.layout = BoxLayout(orientation='vertical')
        # self.print_menu = PrintMenu()
        # self.print_menu.print_function()
        # self.layout.add_widget(self.print_menu.print_popup)
        # self.add_widget(self.layout)

        self.layout = PrintMenu()
        self.add_widget(self.layout)


if __name__ == '__main__':
    KioskApp().run()
