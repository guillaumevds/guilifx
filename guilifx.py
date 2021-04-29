#!/usr/bin/python3

# EDIT THIS
lifx_token = "INSERT_YOUR_TOKEN_HERE"

# DO NOT EDIT BELOW

from requests import get as req_get, put as req_put
from threading import Thread
from PyQt5.Qt import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSlider, QColorDialog

# URL and auth header
lifx_base_url = "https://api.lifx.com/v1/lights"
lifx_headers = {"Authorization": "Bearer %s" % lifx_token}

# functions to call LIFX API
get_all_lights = lambda: req_get("%s/all" % lifx_base_url, headers=lifx_headers).json()
fn_light_set_state_sync = lambda light_id, d: req_put("%s/%s/state" % (lifx_base_url, ("id:%s"%(light_id)) if light_id != "all" else "all"), headers=lifx_headers, data=d)
fn_light_set_brightness =  lambda light_id, brightness: fn_light_set_state(light_id, {"power":"on", "brightness": brightness})
fn_light_set_on_off = lambda light_id, target_state: fn_light_set_state(light_id, {"power": target_state})
fn_light_set_color = lambda light_id, color: fn_light_set_state(light_id, {"power":"on", "color": "rgb:%s,%s,%s" % (color.red(), color.green(), color.blue())})
fn_light_set_state = lambda *args: Thread(target=fn_light_set_state_sync, args=args).start()

# create app and layout
qtapp = QApplication([])
layout = QGridLayout()

# retrieves all lights - for each light creates qt widgets, and add them to the layout
for i, light in enumerate(sorted([{"id":"all", "brightness": 0.5, "label": "All"}] + get_all_lights(), key=lambda o: o.get("label").lower())):
    label = QLabel(light.get("label"))
    button_on, button_off = QPushButton("ON"), QPushButton("OFF")
    button_on.clicked.connect(lambda state, light_id=light.get("id"), target_state="on": fn_light_set_on_off(light_id, target_state))
    button_off.clicked.connect(lambda state, light_id="%s" % light.get("id"), target_state="off": fn_light_set_on_off(light_id, target_state))
    layout.addWidget(label, i, 0)
    layout.addWidget(button_on, i, 1)
    layout.addWidget(button_off, i, 2)
    slider = QSlider()
    slider.sliderReleased.connect(lambda light_id=light.get("id"), slider=slider: fn_light_set_brightness(light_id, (slider.value()+1)/100.0) )
    slider.setValue((light.get("brightness") * 100) - 1)
    button_set_color = QPushButton("Set Color")
    button_set_color.clicked.connect(lambda state, light_id=light.get("id"): fn_light_set_color(light_id, color=QColorDialog.getColor()))
    layout.addWidget(button_set_color, i, 3)
    layout.addWidget(slider, i, 4)

# create and show window
window = QWidget()
window.setWindowTitle("GUILIFX")
window.setLayout(layout)
window.show()
qtapp.exec_()

