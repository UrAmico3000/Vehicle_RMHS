from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.graphics import Color, Ellipse, Line
from math import radians

class CustomGauge(Widget):
    min = NumericProperty(0)
    max = NumericProperty(100)
    value = NumericProperty(0)
    units = StringProperty("")
    line_color = ListProperty([0, 1, 0, 1])  # Default green color

    def __init__(self, **kwargs):
        super(CustomGauge, self).__init__(**kwargs)
        self.bind(value=self.update_gauge)
        self.bind(pos=self.update_gauge)
        self.bind(size=self.update_gauge)
        self.update_gauge()

    def update_gauge(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Draw the background arc
            Color(0.2, 0.2, 0.2, 1)  # Dark gray background
            Line(circle=(self.center_x, self.center_y, self.width / 2, 0, 360), width=2)
            # Draw the value arc
            Color(*self.line_color)
            angle_end = 360 * (self.value - self.min) / (self.max - self.min)
            Line(circle=(self.center_x, self.center_y, self.width / 2, 0, angle_end), width=4)
