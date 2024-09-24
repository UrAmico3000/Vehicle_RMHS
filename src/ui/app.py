# app.py

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.lang import Builder
import json
from readOBDvalues import OBDReader
from custom_gauge import CustomGauge  # Import the custom gauge

Builder.load_file('main.kv')

class MainScreen(Screen):
    pass

class VehicleRMHSApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        self.obd_reader = OBDReader()
        Clock.schedule_interval(self.update_gui, 0.5)
        return sm

    def update_gui(self, dt):
        json_data = self.obd_reader.get_json_data()
        try:
            obd_data = json.loads(json_data)
            main_screen = self.root.get_screen('main')
            main_screen.ids.rpm_gauge.value = obd_data['rpm']
            main_screen.ids.speed_gauge.value = obd_data['speed']
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    VehicleRMHSApp().run()
