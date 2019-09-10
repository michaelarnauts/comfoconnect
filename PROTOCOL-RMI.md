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
| 0x1C      | 1                     | FILTER            | Counts the days since last filter change

        "TEMPHUMCONTROL": 0x1D,
        "VENTILATIONCONFIG": 0x1E,
        "NODECONFIGURATION": 0x20,
        "TEMPERATURESENSOR": 0x21,
        "HUMIDITYSENSOR": 0x22,
        "PRESSURESENSOR": 0x23,
        "PERIPHERALS": 0x24,
        "ANALOGINPUT": 0x25,
        "COOKERHOOD": 0x26,
        "POSTHEATER": 0x27,
        "COMFOFOND": 0x28,

# General commands
There are three commands which always exist on a given Unit


# Overview of known CnRmiRequests:

The request and response are in little endian format (eg. `0x5802` => `0x258` => 600)

This is a list of known commands:

| Command                            | Description                                                                     |
|------------------------------------|---------------------------------------------------------------------------------|
| `8415 0101 0000 0000 0100 0000 00` | Switch to fan speed away                                                        |
| `8415 0101 0000 0000 0100 0000 01` | Switch to fan speed 1                                                           |
| `8415 0101 0000 0000 0100 0000 02` | Switch to fan speed 2                                                           |
| `8415 0101 0000 0000 0100 0000 03` | Switch to fan speed 3                                                           |
| `8415 0106 0000 0000 5802 0000 03` | Bosst mode: start for 10m (= 600 seconds = `0x0258`)                            |
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

This is a list of known data requests:

| Request                            | Response                                                | Description              |
|------------------------------------|---------------------------------------------------------|--------------------------|
| `0101 0110 08`                     | `ComfoAir Q450 B R RF ST Quality\x00`                   | Get HRU Type             |
| `0101 0110 0b`                     | `471502004\x00`                                         | Get Article Number       |
| `0201 0101 1503 0406 0507`         | `\x02BEA004185030000\x00\x00\x10\x10\xc0\x02\x00T\x10@` | Get Serial Number and maybe some other stuff |
| `8715 01`                          | Big response with all Timerreasons glued together       | Read out current Timers for the given   |


```
A: General: Countdown until next fan speed change (`52020000` = 00000252 -> 594 seconds)
S: Fans: Fan speed setting: `0000` (away), `0100`, `0200` or `0300` (configured from app)
B: Fans: Fan speed setting: `0000` (away), `0100`, `0200` or `0300` (configured from remote)
C: Operating mode: `00` (auto), `01` (manual)
D: Configured boost duration
E: Remaining boost duration
```

Unknown messages:

| Request                      | Response                                                   | Description              |
|------------------------------|------------------------------------------------------------|--------------------------|
| `0117 0110 02`               | `\x01`                                                     | *Unknown*                |
| `0117 0210 02`               | `\x00`                                                     | *Unknown*                |
| `0120 0110 06`               | `\x00`                                                     | *Unknown*                |
| `0124 0110 0b`               | `\x00`                                                     | *Unknown*                |
| `0125 0010 03`               | `\x00`                                                     | *Unknown*                |
| `8015 0101`                  | `\x01\x00\x00\x00\x80Q\x01\x00\xff\xff\xff\xff\x01`        | *Unknown*                |
| `8315 0101`                  | `\x01\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x01` | *Unknown*                |
| `8315 0102`                  | `\x01\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x03` | *Unknown*                |
| `8615 01`                    | `\x01\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x02\x01\x00\x00\x00\x80Q\x01\x00\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00` | *Unknown* |
| `8715 05`                    | `\x01\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x00\x00\x00\x01` | *Unknown*            |
