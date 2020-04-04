Overview of known pdids:

| pdid | type | description                                                                                            |
|------|------|--------------------------------------------------------------------------------------------------------|
| 49   | 1    | Operating mode (`01` = limited manual, `05` = unlimited manual, `ff` = auto) |
| 56   | 1    | Operating mode (`01` = unlimited manual, `ff` = auto) |
| 65   | 1    | Fans: Fan speed setting (`00` (away), `01`, `02` or `03`) |
| 81   | 3    | General: Countdown until next fan speed change (`52020000` = 00000252 -> 594 seconds) |
| 117  | 1    | Fans: Exhaust fan duty (`1c` = 28%) |
| 118  | 1    | Fans: Supply fan duty (`1d` = 29%) |
| 119  | 2    | Fans: Exhaust fan flow (`6e00` = 110 m³/h) |
| 120  | 2    | Fans: Supply fan flow (`6900` = 105 m³/h) |
| 121  | 2    | Fans: Exhaust fan speed (`2d04` = 1069 rpm) |
| 122  | 2    | Fans: Supply fan speed (`5904` = 1113 rpm) |
| 128  | 2    | Power Consumption: Current Ventilation (`0f00` = 15 W)  |
| 129  | 2    | Power Consumption: Total year-to-date (`1700` = 23 kWh) |
| 130  | 2    | Power Consumption: Total from start (`1700` = 23 kWh) |
| 144  | 2    | Preheater Power Consumption: Total year-to-date (`1700` = 23 kWh) |
| 145  | 2    | Preheater Power Consumption: Total from start (`1700` = 23 kWh) |
| 146  | 2    | Preheater Power Consumption: Current Ventilation (`0f00` = 15 W)  |
| 192  | 2    | Days left before filters must be replaced (`8200` = 130 days) |
| 209  | 6    | Current RMOT (`7500` = 117 -> 11.7 °C) |
| 213  | 2    | Avoided Heating: Avoided actual: (`b901` = 441 -> 4.41 W) |
| 214  | 2    | Avoided Heating: Avoided year-to-date: (`dd01` = 477 kWh) |
| 215  | 2    | Avoided Heating: Avoided total: (`dd01` = 477 kWh) |
| 216  | 2    | Avoided Cooling: Avoided actual: (`b901` = 441 -> 4.41 W) |
| 217  | 2    | Avoided Cooling: Avoided year-to-date: (`dd01` = 477 kWh) |
| 218  | 2    | Avoided Cooling: Avoided total: (`dd01` = 477 kWh) |
| 221  | 6    | Temperature & Humidity: Supply Air (`aa00` = 170 -> 17.0 °C) PostHeaterTempAfter |
| 227  | 1    | Bypass state (`64` = 100%) |
| 274  | 6    | Temperature & Humidity: Extract Air (`ab00` = 171 -> 17.1 °C) |
| 275  | 6    | Temperature & Humidity: Exhaust Air (`5600` = 86 -> 8.6 °C) |
| 276  | 6    | Temperature & Humidity: Outdoor Air (`3c00` = 60 -> 6.0 °C) |
| 278  | 6    | PostHeaterTempBefore |
| 290  | 1    | Temperature & Humidity: Extract Air (`31` = 49%) |
| 291  | 1    | Temperature & Humidity: Exhaust Air (`57` = 87%) |
| 292  | 1    | Temperature & Humidity: Outdoor Air (`43` = 67%) |
| 294  | 1    | Temperature & Humidity: Supply Air (`23` = 35%) |
| 785  | 0    | ComfoCoolCompressor State |

Unknown/uncertain messages:

| pdid | type | description                                                                                            |
|------|------|--------------------------------------------------------------------------------------------------------|
| 16   | 1    | *Unknown* (`01`) |
| 33   | 1    | *Unknown* (`01`) |
| 37   | 1    | *Unknown* (`00`) |
| 53   | 1    | *Unknown* (`ff`) |
| 66   | 1    | *Unknown* (`00`) |
| 67   | 1    | *Unknown* (`00`) |
| 70   | 1    | *Unknown* (`00`) |
| 71   | 1    | *Unknown* (`00`) |
| 82   | 3    | *Unknown* (`ffffffff`) |
| 85   | 3    | *Unknown* (`ffffffff`) |
| 86   | 3    | *Unknown* (`ffffffff`) |
| 87   | 3    | *Unknown* (`ffffffff`) |
| 176  | 1    | *Unknown* (`00`) |
| 208  | 1    | *Unknown* (`00`), Unit of temperature |
| 210  | 0    | *Unknown* (`00` = false) |
| 211  | 0    | *Unknown* (`00` = false) |
| 212  | 6    | *Unknown* (`ee00` = 238) |
| 219  | 2    | *Unknown* (`0000`) |
| 224  | 1    | *Unknown* (`03` = 3) |
| 225  | 1    | *Unknown* (`01`) |
| 226  | 2    | *Unknown* (`6400` = 100) |
| 228  | 1    | *Unknown* (`00`) FrostProtectionUnbalance |
| 321  | 2    | *Unknown* (`0700` = 7) |
| 325  | 2    | *Unknown* (`0100` = 1) |
| 337  | 3    | *Unknown* (`26000000` = 2409368) |
| 338  | 3    | *Unknown* (`00000000`) |
| 341  | 3    | *Unknown* (`00000000`) |
| 369  | 1    | *Unknown* (`00`) |
| 370  | 1    | *Unknown* (`00`) |
| 371  | 1    | *Unknown* (`00`) |
| 372  | 1    | *Unknown* (`00`) |
| 384  | 6    | *Unknown* (`0000`) |
| 386  | 0    | *Unknown* (`00` = false) |
| 400  | 6    | *Unknown* (`0000`) |
| 401  | 1    | *Unknown* (`00`) |
| 402  | 0    | *Unknown* (`00` = false) PostHeaterPresent? |
| 416  | 6    | *Unknown* (`70fe` = -400)  Outdoor air temperature |
| 417  | 6    | *Unknown* (`6400` = 100) GHE Ground temperature |
| 418  | 1    | *Unknown* (`00`) GHE State |
| 419  | 0    | *Unknown* (`00` = false) GHE Present|

Overview of the types:

| type | description | remark                                                                                          |
|------|-------------|-------------------------------------------------------------------------------------------------|
| 0    | CN_BOOL     | `00` (false), `01` (true) |
| 1    | CN_UINT8    | `00` (0) until `ff` (255) |
| 2    | CN_UINT16   | `3412` = 1234 |
| 3    | CN_UINT32   | `7856 3412` = 12345678 |
| 5    | CN_INT8     | |
| 6    | CN_INT16    | `3412` = 1234 |
| 8    | CN_INT64    | |
| 9    | CN_STRING   | |
| 10   | CN_TIME     | |
| 11   | CN_VERSION  | |
