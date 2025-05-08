import random
import time
import RobotBridge as rb
from RobotBridge import Comando

porta = rb.selezionaPortaSeriale()
robot = rb.Robot(porta, 115200)

def programma():
    robot.move(Comando.AVANTI, 100)
    robot.delay(1)
    print(robot.ultrasonico)
    pass

try:
    input("Premi Invio per avviare il programma...")
    while True:
        programma()
except KeyboardInterrupt:
    print("\nProgramma Interrotto")
    exit(0)