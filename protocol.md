# Communication protocol between an Arduino and a KRPC code

## Message format

Messages have the format ```X[<>]Y...Y``` Where X codes the type of message:

* K for normal KSP communication
* D for data (flight,etc)
* C for command (control input)
* E for errors

Y...Y is a sequence of n characters, which should be of expected length
The < or > symbol indicates the identity of the sender

* Server to Arduino messages have a ```>```
* Arduino to Server messages have a ```<```

## Standby modes

The standby modes for the Server is ```EXPECTED``` as it is the one that initializes communications. In that mode, it can receive a list of emergency 3-byte commands:

* Emergency abort: ```K!A``` (*in-game abort*)
* Parachutes: ```K!P``` (*in-game release parachutes*)
* Hardware failure ```K!H``` (*IRL PROBLEM!!!*)

The standby mode for the Arduino is ```EXPECTING```. It should be waiting for 3-byte messages of the form ```X>Y```.


## Error handling
### Arduino
Whenever something goes wrong on the Arduino side, it should send the message ```K<E``` and wait for a ```K>R```, then send a ```K<R``` and go to ```EXPECTING```

If the Arduino receives a ```K>E```, it should send a ```K<R``` and go to ```EXPECTING```
### Server
Whenever something goes wrong on the Server side, it should send the message ```K>E``` and wait for a ```K<R``` and go to ```EXPECTED``` mode.

If the Server receives a ```K<E```, it should send a ```K>R``` and then wait for a ```K<R``` and go to ```EXPECTED```

## Arduino Initialization

The Arduino should initialize the Serial connexion with a baud rate of 9600

The Arduino now waits for the server side message

The Arduino checks if > 4 chars are available.
When this happens, it reads it and checks they are
```K>S```. If this is the case, it waits for a second message saying
```K>R``` and sends a ```K<R```

Arduino goes to ```EXPECTING``` mode.

## Server Initialization

The server initializes a Serial connexion with the same baud rate. It sends ```K>S``` then empties the serial buffer on its side, then sends ```K>R```. When the server receives a ```K<R```, the server goes to ```EXPECTED``` mode

***
## **TODO**: verification of the control and data tables
***

## Control interface

### Sending a request from the Server
If the Server is in ```EXPECTED``` mode, it can send a request for control input with the message
```K>C```, going into ```CONTROL``` mode.

The Server waits for 3 chars and checks if they are ```K<C```, signaling the Arduino is ready.

The Server sends a sequence ```C>N``` where N is a byte encoding a number n<256

The Server waits for ```C<1``` meaning the Arduino is ready

The Server sends ```C>A_1...A_N``` where each ```A_i``` is the identifier of a control input (a byte representing an integer n_i < 256)

The Server waits for ```C<2``` meaning the Arduino knows what to do with each input code

The Server waits for a sequence of bytes matching

```C<B_11B_12...B_NlN```

The output is a list of bytes. Bytes ```B_11...B_1l1``` are the number of bytes required to describe the data type of ```A_1``` etc. The length of this list is therefore known in advance. If everything is in order, the handshake to go back to standby is

```K>R```;
```K<R```

### Answering a request from the Arduino

If the Arduino is in ```EXPECTING``` mode and receives a message ```K>C```, it goes into ```CONTROL``` mode.

The Arduino sends ```K<C``` to confirm reception

The Arduino waits for a 3-byte message ```C>N```
N should be read as a one-byte, integer telling it to reserve memory for a string of length N.

Once ready, the Arduino sends ```C<1``` to signal it

The Arduino expects a sequence ```C>A_1...A_N``` telling it which inputs are required and stores it. The Arduino checks that each ```A_i``` is available and sends ```C<2``` if this is the case.
It then sends

```C<B_11B_12...B_NlN```

which encodes the value of each input byte by byte (1 byte for bool, 2 bytes for int, 4 bytes for float). The Arduino then waits for the exit handshake:

```K>R```;
```K<R```

## TODO Data interface
