## DAT300-PyModbus

This project contains a simple implementation of synchrounous MODBUS server that continuously reads data from a input .CSV file and writes to a output .CSV file. The MODBUS server can then be queried by a MODBUS client.

## Code Example
The IOserver is easily run with the following command
```
$ python3 IOserver.py -I "Inputfile.csv" -O "Outputfile.csv"
```
This starts a MODBUS TCP server on localhost with default port 502. The MODBUS Server periodically reads data from the Inputfile and writes data to the Outputfile. Alternatley the command can be written without the -I and -O options and then it just initializes a server with dummy data.

## Motivation

This project was implemented in an effort to generate MODBUS traffic from a Matlab implementation of the often simulated Tenesee-Eastmann process. MODBUS network traffic from the TE-process can for example be useful for testing new intrusion detection system designs aimed at Industrial Control Systems. 

## Installation

This project is implemented using Python3 and PyModbus, both must be installed for this project to run. To run any of the files in the project it is only necssary to download them and run.

The Python3 fork of PyModbus can be found here: https://github.com/bashwork/pymodbus/tree/python3/pymodbus
Documents for PyModbus can for example be found here: http://pymodbus.readthedocs.io/en/latest/examples/index.html

## Options

IOServer.py can be run with several different options/flags set. 

--debug option:
```
$ python3 IOserver.py -D
```
This enables PyModbus built in debug mode. This can be set by either --debug or -D.

--inputfile option:
```
$ python3 IOserver.py -I "Inputfile.csv"
```
This option provides an input file from which the Server initializes its values and updates from. This can be set by set by either --inputfile or -I.  ´
The input file should have the following format:
Address, Discrete Input, Coils, Holding Registers, Input Registers

--read_frequency option:
```
$ python3 IOserver.py -I "Inputfile.csv" -R 5
```
This option allows the user to set the time between file reads/updates of server values from the Inputfile. This option can be set by either --read_frequency or R, the value provided specifies time in seconds.

--no_update option:
```
$ python3 IOserver.py -I "Inputfile.csv" --no_update
```
This option allows you to initialize the data values on the MODBUS server to those of the inputfile, but the MODBUS server does not update the values from the inputfile after it has been initialized.
This option can be set by --no_update.

 --outputfile option:
```
$ python3 IOserver.py -O "Outputfile.csv"
```
This option allows a user to specify an outputfile for the server to write to. If the file already exists the content of the file will be overwritten, if the file does not exist it will be created and data written to it.
It should be noted that when the server writes to a file it always overwrites previous data, it does not append the new data! The data will be output with the same format as required by the inputfile.
This flag can be set by either --outputfile or -O. It should be noted that the Outputfile can be the same file as the Inputfile, however when this is the case, we can not guarantee correctness of data.

--write_frequency option:
```
$ python3 IOserver.py -O "Outputfile.csv" -W 5.1
```
This option allows a user to set the time between file writes. This option can be set by either --write_frequency or -W. The time specified should be in seconds.

--no_output option:
```
$ python3 IOserver.py --no_output
```
When this flag is set the server does not periodically write to an outputfile. This is not the same as not passing the -O flag to the program, when the -O flag is not passed the program writes data periodically to a preset dummyfile.
This option can be set by --no_output.

--use_samefile option:
```
$ python3 IOserver.py -I "Inputfile.csv" -S
```
This flag is the same as setting the inputfile and the outpufile to the same flag e.g. -I "Inputfile.csv" -W "Inputfile.csv". This flag can be set by either --use_samfile or -S.
It should be noted that the correctness of the data in the file can not be guaranteed when this option is set.

--address option:
```
$ python3 IOserver.py -A "192.168.0.1"
```
This option allows the user to specify which IP address the MODBUS server should be started on. This can be set by either --address or -A flags supplied with a valid ip-address.

--port option:
```
$ python3 IOserver.py -P 502
```
This option allows the user to specify which port the MODBUS server should be started on. This can be set by either --port or -P flags supplied with a valid port number.

## Tests

The success of the setup can quickly be tested by starting the IOServer.py 
```
$ python3 IOserver.py -I "CSVtest1.csv" -O "CSVtest4.csv" -P 5020 -D
```
and then running the test script:
```
$ python3 Sync-TestClient.py
```


## License

This project is free to use and modify under the MIT license.

## NOTICE!
All addresses in the input file should start from 1 and be in sequential order
from there. Leaving gaps in the addressing will cause the write_filedata
function to terminate at the first gap.

## LIMITATIONS!
The decision on which input has final say when comparing the contents of the
pymodbus registers and that of the input file was made with the following
reasoning.
As Discrete Input and Input registers are read only tables, the values
contained in the input file to be read overwrites the contents of the pymodbus
Discrete Input and Input registers if they disagree with the current value of
the registers.
For Coils and Holding registers, as they are read/write registers, the current
values of the registers overwrites the values received by the input file.
In summary:
As modifications by a client to the DI and Input registers of a server are not
allowed, the values of the input files are taken as updates by a I/O system and
are kept. However, as Coils and Holding registers are read/write we assume that
we want to keep updates made by the client to the server, therefore we keep the
servers version and disregard the values of the input file for these registers.
