# custom_gauge.py

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.graphics import Color, Ellipse, Line, Triangle, PushMatrix, PopMatrix, Rotate
from math import radians

class CustomGauge(Widget):
    min = NumericProperty(0)
    max = NumericProperty(100)
    value = NumericProperty(0)
    units = StringProperty("Unit")
    line_color = ListProperty([1, 0, 0, 1])  # Default: red

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(value=self.update_gauge, size=self.update_gauge, pos=self.update_gauge)
        self.update_gauge()

    def update_gauge(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Set the size for the gauge as the smaller dimension (width or height)
            gauge_size = min(self.width, self.height) * 0.9  # To keep some padding
            radius = gauge_size / 2
            center_x, center_y = self.center

            # Draw the outer circle
            Color(0.2, 0.2, 0.2, 1)  # Dark gray background
            Ellipse(pos=(center_x - radius, center_y - radius), size=(gauge_size, gauge_size))

            # Draw the arc representing the value
            Color(*self.line_color)
            angle_end = 360 * (self.value - self.min) / (self.max - self.min)
            Line(circle=(center_x, center_y, radius, 0, angle_end), width=4)

            # Draw the needle
            needle_angle = angle_end - 90  # Adjust for starting at the top
            self.draw_needle(needle_angle, radius)

    def draw_needle(self, angle, radius):
        # Draw a triangle for the needle
        Color(1, 0, 0, 1)  # Red needle
        needle_length = radius * 0.75  # Make the needle 75% of the radius
        needle_width = radius * 0.05   # Needle width relative to gauge size

        PushMatrix()
        Rotate(angle=angle, origin=(self.center_x, self.center_y))
        Triangle(points=[
            self.center_x, self.center_y,  # Center point
            self.center_x - needle_width, self.center_y + needle_length,  # Left point of the triangle
            self.center_x + needle_width, self.center_y + needle_length  # Right point of the triangle
        ])
        PopMatrix()
