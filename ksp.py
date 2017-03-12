import krpc
from toolbox import *
from time import sleep
from math import exp,sqrt

def ksp_initialize():
    print "Initialization of KRPC connection"
    print "Output structure: (connection,vessel,control,autopilot)"
    conn = krpc.connect(name='Arduino_Interface')
    vessel = conn.space_center.active_vessel
    control = vessel.control
    ap = vessel.auto_pilot
    return (conn,vessel,control,ap)
