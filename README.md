# esp8266-pichler
ESP8266 based gateway between Pichler LG350 (home ventilation system) and MQTT.

!!!!!! Warning !!!!!!!! 
* Use on your own risk, this is no approved accessory!
* Connecting the Modbus RTU means opening the device, which potentially exposes also some live wires (230V) in close proximity!
* Running the ventilation system with modified parameters could not just void the device warranty. But in case you are not an expert, you might also risk all kind of humidity problems in your house, creating mildew etc.
!!!!!! Warning !!!!!!!! 

This little project was basically a workaround. Initially I planned to use an Raspberry Pi4 with an MAX485 to talk to the modbus. But it turned out, the MAX485 needs a TXEnable control line when transmitting. And especially releasing this signal when receiving, otherwise the bus will be blocked. After some messing around, I found how to enable a RTS signal for the Pi's UART. However, the RTS timing is wrong. Using just a GPIO instead was to slow in a python based environment on the PI. Getting another RS485 transceiver is not so easy with all lock'ed down in 2020 now. But luckily I had still an ES8266 module at home. So publishing this project is more for educational purposes and will not be maintianed in future, since I prefer to go back to the PI when possible. 
zubehör
On the hardware side, I'm using a ESP8266 NodeMCU and a simple MAX485 based transceiver for MODBUS RTU. Connection is:
* GPIO1 (UART TX) - MAX485 DE
* GPIO3 (UART RX) - MAX485 RO
* GPIO15 (TX ENABLE) - MAX485 RE + DE (since one is inverted internally they can be tight together)
The whole codebase is likely also working on a ESP32. 

For the modbus library, I forked https://github.com/techbase123/micropython-modbus. However, my Micropython 1.13 for ESP8266 does not have a uart.wait_tx_done() function. Instead I'm using a calculation how long it takes to send the data to control the TX enable GPIO. It is a bit risky, but on my device it works reasonable well. The TX enable is about 1 ms to late deasserted, but thats still in time to get ready to receive data. 
read_input_registers() works only up to 5 registers. For larger reads, it seems there is some strange behavoir on the UART receiving side. But for my application, 5 registers are good enough. The MQTT transfer uses anyway just one register at the time. 

Controlling the Pichler LG350 is realtively straight forward. But I'm not sure how much they like if I disclose the whole register list. Therefore please ask via your own support contacts for the register list. I got a Excel list, but some of the parameters need some addtional calculation (offset/scaling), this is background of the param1/2 in the list. 

I'm using all of this just to read some parameters like temperatures or switch off/on the device. Please do not mess with other parameters without appropriate training. 

The mainloop is a little bit unsophisticated. There could be for sure more error handling added, in case the Wifi connection breaks, in case cable problems etc. 

By the way, behind MQTT I'm using some InfluxDB + Grafana on a PI to draw some nice graphs.
