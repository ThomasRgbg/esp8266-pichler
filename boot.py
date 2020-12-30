# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl

import network
webrepl.start()
gc.collect()


wlan = network.WLAN(network.STA_IF)
wlan.active(True) 
wlan.scan()
wlan.connect('ZZZZ', 'XXXXX')
wlan.ifconfig()

