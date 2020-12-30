
# Format
# "Register name : [ register_value, add_value, multiply_value, export ]

# Redaced list. Please ask the manufacturer (Pichler) for the list of modbus registers. 
# Or search on your own on the internet. 


pichler_input_registers = {
    "status_betrieb" : [48, 0, 1, True ],        # 0=startup 1=Standby 2=Anlauf 3=Betrieb 4=Nachlauf 5=Standby 6=Testmodus
    }

