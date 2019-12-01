# ComfoControl CAN/RMI Protocol
This document tries to outline the protocol as used by the newer "Q"-Models. Please note that some stuff might be version dependent, especially ranges. My findings are based on ~R1.6.2
Two basic assumptions:
 - Your airflow unit is m³/h
 - Your temperature is measured in °C

If your ventilation is set to something else you need to try it out

# Quick Overview of the network:
Speed is 100kb/s, no CAN-FD but extended ID's are used (one exception: firmware uploading)
Each device has an unique node-id smaller than 0x3F or 64. If a device detects that another device is writing using "his" id, the device will change its id

Nodes send a periodic message to 0x10000000 + Node-ID with DLC 0 or 4

All PDO's (= sensors, regular data to be transferred, PUSH-Model) are sent with the following ID:
 `PDO-ID << 14 + 0x40 + Node-ID`

Firmware-Updates are sent using 11-bit IDs or 1F800000

RMI-Commands are sent and received using extended-IDs:
```
    1F000000
    + SrcAddr        << 0 6 bits  source Node-Id
    + DstAddr        << 6 6 bits  destination Node-Id
    + AnotherCounter <<12 2 bits  we dont know what this is, set it to 0, everything else wont work
    + MultiMsg       <<14 1 bit   if this is a message composed of multiple CAN-frames
    + ErrorOccured   <<15 1 bit   When Response: If an error occured
    + IsRequest      <<16 1 bit   If the message is a request
    + SeqNr          <<17 2 bits, request counter (should be the same for each frame in a multimsg), copied over to the response
```
Some Examples: 
```
1F015057: 11111 0000 0001 0101 00 0001 010111 multi-msg request with SeqNr = 0
1F011074: 11111 0000 0001 0001 00 0001 110100 single-msg request with SeqNr = 0
1F071074: 11111 0000 0111 0001 00 0001 110100 single-msg request with SeqNr = 3

1F005D01: 11111 0000 0000 0101 11 0100 000001 no-error multi-msg response, seqnr = 0
1F001D01: 11111 0000 0000 0001 11 0100 000001 no-error single-msg response, seqnr = 0
1F009D01: 11111 0000 0000 1001 11 0100 000001 error, seqnr = 0
```

# Encoding an RMI command/message into CAN-Messages
There are two ways of messaging them:
1.  If the message is less or equal than 8 bytes, it will be sent unfragmented.
    CAN-Data = RMI-Data
    MultiMsg = 0

    Example:
    Request: `01 1D 01 10 0A` (Get (`0x01`) from Unit `1D 01` (`TEMPHUMCONTROL 01`) exact value (`10`) variable `0A` (`Target Temperature Warm`))
    Response: `E6 00` little-endian encoded, `0x00E6 = 230 = 23.0°C`
    ```
        can1  1F011074   [5]  01 1D 01 10 0A
        can1  1F001D01   [2]  E6 00
    ```

2.  If the message is longer than 8 bytes, it will be fragmented into 7-byte blocks
    Each block is prepended with the index (starting at 0) of the block. If the block is the last to come, 0x80 is added to the first byte.
   
    Example:
    CMI-Request: `80 03 01`, answer `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`
    ```
        can1  1F011074   [3]  80 03 01  # I send
        can1  1F005D01   [8]  00 00 00 00 00 00 00 00  # Answer
        can1  1F005D01   [8]  01 00 00 00 00 00 00 00
        can1  1F005D01   [8]  02 00 00 00 00 00 00 00
        can1  1F005D01   [8]  03 00 00 00 00 00 00 00
        can1  1F005D01   [5]  84 00 00 00 00
    ```

# Enums in the network
If an error occures the reason maybe one of the following:

| Number    | Description                                                                                               |
|-----------|-----------------------------------------------------------------------------------------------------------|
| 11        | Unknown Command                                                                                           |
| 12        | Unknown Unit                                                                                              |
| 13        | Unknown SubUnit                                                                                           |
| 15        | Type can not have a range                                                                                 |
| 30        | Value given not in Range                                                                                  |
| 32        | Property not gettable or settable                                                                         |
| 40        | Internal error                                                                                            |
| 41        | Internal error, maybe your command is wrong                                                               |

Please note that this list is not complete.

For types please check [PROTOCOL-PDO.md](PROTOCOL-PDO.md)

# Units
The Ventilation is seperated into multiple Units, and sometimes even SubUnits. Here is a list of some existing units:

| ID        | Amount of SubUnits    | Name              | Responsible for                                                                               |
|-----------|-----------------------|-------------------|-----------------------------------------------------------------------------------------------|
| 0x01      | 1                     | NODE              | Represents the general node with attributes like serial nr, etc.                              |
| 0x02      | 1                     | COMFOBUS          | Unit responsible for comfobus-communication. Probably stores the ID's of connected devices.   |
| 0x03      | 1                     | ERROR             | Stores errors, allows errors to be reset                                                      |
| 0x15      | 10                    | SCHEDULE          | Responsible for managing Timers, the schedule, etc. Check here for level, bypass etc.         |
| 0x16      | 2                     | VALVE             | ??? Bypass PreHeater and Extract                                                              |
| 0x17      | 2                     | FAN               | Represents the two fans (supply, exhaust)                                                     |
| 0x18      | 1                     | POWERSENSOR       | Counts the actual wattage of ventilation and accumulates to year and since factory reset      |
| 0x19      | 1                     | PREHEATER         | Represents the optional preheater                                                             |
| 0x1A      | 1                     | HMI               | Represents the Display + Buttons                                                              |
| 0x1B      | 1                     | RFCOMMUNICATION   | wireless-communication with attached devices                                                  |
| 0x1C      | 1                     | FILTER            | Counts the days since last filter change                                                      |
| 0x1D      | 1                     | TEMPHUMCONTROL    | Controls the target temperature, if its cooling or heating period and some settings           |
| 0x1E      | 1                     | VENTILATIONCONFIG | Responsible for managing various configuration options of the ventilation                     |
| 0x20      | 1                     | NODECONFIGURATION | Manages also some options                                                                     |
| 0x21    	| 6                     | TEMPERATURESENSOR | Represents the 6 temperature sensors in the ventilation                                       |
| 0x22      | 6                     | HUMIDITYSENSOR    | Represents the 6 humidity sensors                                                             |
| 0x23      | 2                     | PRESSURESENSOR    | Represents both pressure sensors                                                              |
| 0x24      | 1                     | PERIPHERALS       | Stores the ID of the ComfoCool attached, can reset peripheral errors here                     |
| 0x25      | 4                     | ANALOGINPUT       | Provides data and functionality for the analog inputs, also the scaling for the voltages      |
| 0x26      | 1                     | COOKERHOOD        | "Dummy" unit, probably represents the ComfoHood if attached                                   |
| 0x27      | 1                     | POSTHEATER        | Represents the optional post heater attached (temperature sens, config)                       |
| 0x28      | 1                     | COMFOFOND         | "Dummy" unit, represents the optional comfofond                                               |

# General commands
There are three commands which always exist on a given Unit:
 - `0x01`: Read single property:
   
   This command reads a single property identified by the Unit, SubUnit and Property Id.
   Each writable property may have a definitionrange & recommended step size which are also accesible

   The syntax is: `01 UnitId SubUnitId GetType PropertyId`
   The answer is depended on the type of the property and the GetType. If the value, range and step (everything) is requested, the answer is: Value, lower boundry of range, upper boundry of range, step size.

   Example: Get maintainer password: `01 20 01 10 03`, answer: `34 32 31 30 00` (4210\0)\
   Unit is `NODECONFIGURATION`, first SubUnit, PropertyId `03`

 - `0x02`: Read multiple property:
   
   This command allows to read multiple propertys within one request, given that the caller knows the type of each.
   As this command can be replaced by multiple calls to 0x01, we omit it here.

 - `0x03`: Set a single property:

   This commands sets one property to the given value. The value needs to be in the range as identified within 0x01, otherwise an error of 30 is returned. The step size, however, is not checked.
   
   Syntax: `03 UnitId SubUnitId PropertyId Value`

   Example: `03 1D 01 04 00`\
   Unit is `TEMPHUMCONTROL`, first SubUnit, PropertyId: `04`\
   Sets the Property "Sensor ventilation: Temperature passive" to off

All other commands are >= 0x80 and dependent on the SubUnit.
One example for a custom, unit dependent command is 0x85 from Unit `SCHEDULE` (`15`). It disables a given Timer Entry for a timer, in the example it allows the bypass to be returning to its automatic position:\
`85 15 02 01`

Please do not try to run command 0x80, 0x82 on NodeConfiguration (0x20), they will probably break your configuration, and even worse would be calling ANY >= 0x80 command on 0x01. \
It can probably completely brick your ventilation. (it enters factory mode or tries to perform an update)

# Some interesting properties:

| Unit      | PropId    | Access  | Format    | Description                                                 |
|-----------|-----------|---------|-----------|-------------------------------------------------------------|
| 0x1E      | 0x03      | rw      | UINT16    | Ventilation speed in "Away" Level                           |
| 0x1E      | 0x04      | rw      | UINT16    | Ventilation speed in "Low" Level                            |
| 0x1E      | 0x05      | rw      | UINT16    | Ventilation speed in "Medium" Level                         |
| 0x1E      | 0x06      | rw      | UINT16    | Ventilation speed in "High" Level                           |
| 0x1E      | 0x18      | rw      | INT16     | Disbalance in percent                                       |
| 0x01      | 0x04      | ro      | STRING    | Serial number                                               |
| 0x01      | 0x08      | ro      | STRING    | Typenbezeichnung                                            |
| 0x01      | 0x0B      | ro      | STRING    | Article number                                              |
| 0x01      | 0x0D      | ro      | STRING    | Country (Manufacturing or Current?)                         |
| 0x01      | 0x14      | ro      | STRING    | "ComfoAirQ"                                                 |
| 0x1D      | 0x02      | rw      | INT16     | RMOT for cooling period                                     |
| 0x1D      | 0x03      | rw      | INT16     | RMOT for heating period                                     |
| 0x1D      | 0x04      | rw      | UINT8     | Passive temperature control (off, autoonly, on)             |
| 0x1D      | 0x05      | rw      | UINT8     | unknown (off, autoonly, on)                                 |
| 0x1D      | 0x06      | rw      | UINT8     | Humidity comfort control (off, autoonly, on)                |
| 0x1D      | 0x07      | rw      | UINT8     | Humidity protection (off, autoonly, on)                     |
| 0x1D      | 0x08      | rw      | UINT8     | unknown (off, autoonly, on)                                 |
| 0x1D      | 0x0A      | rw      | INT16     | Target temperature for profile: Heating                     |
| 0x1D      | 0x0B      | rw      | INT16     | Target temperature for profile: Normal                      |
| 0x1D      | 0x0C      | rw      | INT16     | Target temperature for profile: Cooling                     |

# Basic list of commonly-used commands:

This is a list of known commands:

| Command                            | Description                                                                     |
|------------------------------------|---------------------------------------------------------------------------------|
| `8415 0101 0000 0000 0100 0000 00` | Switch to fan speed away                                                        |
| `8415 0101 0000 0000 0100 0000 01` | Switch to fan speed 1                                                           |
| `8415 0101 0000 0000 0100 0000 02` | Switch to fan speed 2                                                           |
| `8415 0101 0000 0000 0100 0000 03` | Switch to fan speed 3                                                           |
| `8415 0106 0000 0000 5802 0000 03` | Boost mode: start for 10m (= 600 seconds = `0x0258`)                            |
| `8515 0106`                        | Boost mode: end                                                                 |
| `8515 0801`                        | Switch to auto mode                                                             |
| `8415 0801 0000 0000 0100 0000 01` | Switch to manual mode                                                           |
| `8415 0601 00000000 100e0000 01`   | Set ventilation mode: supply only for 1 hour                                    |
| `8515 0601`                        | Set ventilation mode: balance mode                                              |
| `8415 0301 00000000 ffffffff 00`   | Set temperature profile: normal                                                 |
| `8415 0301 00000000 ffffffff 01`   | Set temperature profile: cool                                                   |
| `8415 0301 00000000 ffffffff 02`   | Set temperature profile: warm                                                   |
| `8415 0201 00000000 100e0000 01`   | Set bypass: activated for 1 hour                                                |
| `8415 0201 00000000 100e0000 02`   | Set bypass: deactivated for 1 hour                                              |
| `8515 0201`                        | Set bypass: auto                                                                |
| `031d 0104 00`                     | Set sensor ventilation: temperature passive: off                                |
| `031d 0104 01`                     | Set sensor ventilation: temperature passive: auto only                          |
| `031d 0104 02`                     | Set sensor ventilation: temperature passive: on                                 |
| `031d 0106 00`                     | Set sensor ventilation: humidity comfort: off                                   |
| `031d 0106 01`                     | Set sensor ventilation: humidity comfort: auto only                             |
| `031d 0106 02`                     | Set sensor ventilation: humidity comfort: on                                    |
| `031d 0107 00`                     | Set sensor ventilation: humidity protection: off                                |
| `031d 0107 01`                     | Set sensor ventilation: humidity protection: auto                               |
| `031d 0107 02`                     | Set sensor ventilation: humidity protection: on                                 |
