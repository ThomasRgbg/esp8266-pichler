from machine import Pin, I2C, reset, RTC, Timer, ADC, WDT, UART, unique_id
import time
from ubinascii import hexlify

from umqtt.robust import MQTTClient

import uModBusSerial

from pichler_registers import pichler_input_registers

#####
# Schematic/Notes
######

# GPIO1 UART TX
# GPIO3 UART RX
# GPIO15 TX enable + RX not-enable 

#####
# Watchdog - 60 seconds, need to be larger then loop time below. Works only on ESP32
# Don't forget to enable wdt.feed() below
#####

# wdt = WDT(timeout=60000)

#####
# RS485/modbus via UART
#####

modbus = uModBusSerial.uModBusSerial(uart_id=0, baudrate=19200, data_bits=8, parity=0, stop_bits=1, pins=[Pin(1),Pin(3)], ctrl_pin=15)

#####
# LG350 connection
#####

class PichlerLG350:
    def __init__(self, modbus):
        self.modbus = modbus

    @property
    def luftstufe(self):
        value = self.modbus.read_holding_registers(20, 2, 1)[0]
        return value

    @luftstufe.setter
    def luftstufe(self, value):
        value = int(value)
        if value >= 0 and value < 4:
            self.modbus.write_single_register(20, 2, value)
        else:
            print("luftstufe out of range")

    def get_input_registers(self):
        results = {}
        for name, params in pichler_input_registers.items():
            if params[3] == True:
                value = self.modbus.read_input_registers(20, params[0], 1)[0]
                value += params[1]
                value *= params[2]
                results.update({name: value})
        return results

pichler = PichlerLG350(modbus)

#####
# MQTT connection
#####

class SensorClient:
    def __init__(self, sensor, client_id, server):
        self.sensor = sensor
        self.mqtt = MQTTClient(client_id, server)
        self.name = b'myhome/lueftung'
        self.mqtt.connect()
        self.mqtt.set_callback(self.callback_mqtt_msg)
        self.mqtt.subscribe(self.name + b'/set_luftstufe')

    def publish_luftstufe(self, ls):
        print("Sending luftstufe : {0}".format(ls))
        self.mqtt.publish(self.name + b'/luftstufe', str(ls))

    def publish_generic(self, name, value):
        print("Sending {0} = {1}".format(name, value))
        self.mqtt.publish(self.name + b'/' + bytes(name, 'ascii'), str(value))

    def callback_mqtt_msg(self, topic, msg):
        print("received MQTT message")
        print(topic, msg)
        if topic == self.name + b'/set_luftstufe':
            pichler.luftstufe = int(msg)

def connect_mqtt():
    print("try to connect to MQTT server")
    try:
        sc_try = SensorClient('lueftung', hexlify(unique_id()), '192.168.0.1')
    except:
        sc_try = None

    return sc_try

#####
# Main loop
#####

def mainloop():
    count = 1
    sc = connect_mqtt()
    errcount = 0 
    while True:
        if sc is None:
            errcount += 1
            sc = connect_mqtt()
            continue
        else:
            try:
                sc.publish_luftstufe(pichler.luftstufe)

                values = pichler.get_input_registers()
                for name, value in values.items():
                    sc.publish_generic(name, value)

                sc.mqtt.check_msg()

            except:
                errcount += 1

        print("Error counter: {0}".format(errcount))

        if errcount > 20:
            reset()

        # wdt.feed()

        time.sleep(60)

mainloop()

