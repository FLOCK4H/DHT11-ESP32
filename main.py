"""
=====================================================
    This project aims to check the current weather
    using the module DHT-11 and an ESP32 WROOOM with
    DevKit v1 Board.
=====================================================
"""
from machine import Pin, Timer, PWM
import network
import dht
import urequests
state = "off"

red_led = PWM(Pin(0), freq=5000)
red_led.duty(0)

def link_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        wifi.connect("ESSID", "Password")
        while not wifi.isconnected():
            pass

# def set_bulb(mode):
#      """
#          Uncomment this function if you want to switch your bulb (if you have one with wifi) on or off with a button press
#      """
#     global state
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     data = "state=on" if mode == "on" else "state=off"
#     state = "on" if mode == "on" else "off"
#     try:
#         res = urequests.post('api_server_url', headers=headers, data=data)
#         res.close()
#     except Exception as e:
#         print(e)

def listen_for_boot():
    boot_pin = Pin(0, Pin.IN, Pin.PULL_UP)

    def button_pressed(pin):
        action = set_bulb("on") if state == "off" else set_bulb("off")

    boot_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

def weather_station():
    dht_sensor = dht.DHT11(Pin(2))  
    dht_sensor.measure()
    temp = dht_sensor.temperature() 
    hum = dht_sensor.humidity()

    def send_data():
        try:
            res = urequests.post('http://raspify.pagekite.me/weather', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=f"inst=set&temp={temp}&hum={hum}")
            res.close()
        except Exception as e:
            print(e)

    send_data()

def timer_handler(t):
    weather_station()    

def main():
    link_wifi()

    listen_for_boot()
    weather_station()

    weather_timer = Timer(-1)
    weather_timer.init(period=30000, mode=Timer.PERIODIC, callback=timer_handler)

main()