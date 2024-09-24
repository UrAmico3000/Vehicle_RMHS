# app.py
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import json
from readOBDvalues import OBDReader


Builder.load_file('main.kv')
class MainScreen(Screen):
    pass

class VehicleRMHSApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"  # Optional: Set the theme to Dark or Light
        self.theme_cls.primary_palette = "BlueGray"  # Optional: Set the primary color palette

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))

        self.obd_reader = OBDReader()
        Clock.schedule_interval(self.update_gui, 0.5)  # Update the GUI every 500 milliseconds
        return sm

    def update_gui(self, dt):
        json_data = self.obd_reader.get_json_data()

        try:
            obd_data = json.loads(json_data)
            main_screen = self.root.get_screen('main')

            # Print available ids
            # print("Available IDs:", main_screen.ids.keys())

            # Update the progress bars and labels using 'ids'
            main_screen.ids.rpm_bar.value = obd_data['rpm']
            main_screen.ids.speed_bar.value = obd_data['speed']
            main_screen.ids.rpm_label.text = f"RPM: {obd_data['rpm']}"
            main_screen.ids.speed_label.text = f"Speed: {obd_data['speed']} km/h"

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON or missing keys: {e}")

if __name__ == '__main__':
    VehicleRMHSApp().run()
