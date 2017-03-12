#Library to implement the protocol
from serial import Serial

class ServerException(Exception):
    pass
class ArduinoException(Exception):
    pass
class EmergencyException(Exception):
    pass

class KAPConnection(Serial):
    def __init__(self,address):
        print "Establishing a serial connection with "+address
        Serial.__init__(self,address,timeout=0.1)
        self.mode="INIT"
        print "Attempting a startup handshake with "+address
        self.put("K>S")
        self.readlines()
        self.put("K>R")
        self.expect("K<R")
        self.mode="EXPECTED"
    def put(self,msg):
        self.write(msg.encode('utf-8'))
    def expect(self,expmsg,l=None):
        if l==None:
            l=len(expmsg)
        elif l<len(expmsg):
            raise ServerException
        msg=self.read(l)
        if len(msg)<l:
            raise ServerException
        elif msg[:len(expmsg)]==expmsg:
            return msg
        elif len(msg)==3:
            if msg=="K<E":
                raise ArduinoException
            elif msg[1]=="!":
                self.handle_emergency(msg)

    def request_controls(self,controls):
        if self.mode!="EXPECTED":
            raise ServerException
        self.mode="CONTROL"
        self.put("K>C")
        self.expect("K<C")
        self.put("K>")
        self.put(chr(len(controls)))
        self.expect("C<1")
        self.put("C>")
        l=2
        for c in controls:
            self.put(chr(c.id))
            l+=c.data_volume
        self.expect("C<2")
        data=self.expect("C<",l)
        return data


class Control:
    def __init__(self,Name,Type,ID,control,command):
        self.name=Name
        self.type=Type
        self.id=ID
        self.control=control
        self.command=command
        if self.type=="bool":
            self.data_volume=1
        elif self.type=="int":
            self.data_volume=2
        elif self.type=="float":
            self.data_volume=4
    def update(self,value):
        exec("self.control."+self.command+"="+str(value))
