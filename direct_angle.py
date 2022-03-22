from datetime import datetime
import multiprocessing
from multiprocessing import Process, Queue, Value, Manager
from multiprocessing.managers import BaseManager
from tracemalloc import start
from unittest import result
from socketio import Client
import json
import requests
import RPi.GPIO as GPIO
import os
import signal
from time import sleep
from customLib import HCSR04, MPU6050, capture_and_predict
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DIR = 20   # Direction GPIO Pin
STEP = 21  # Step GPIO Pin
DIR_PUMP = 26
STEP_PUMP = 19
DIR_CAM = 13
STEP_CAM = 6
PUMP_IN = 4
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(DIR_CAM, GPIO.OUT)
GPIO.setup(STEP_CAM, GPIO.OUT)
GPIO.setup(DIR_PUMP, GPIO.OUT)
GPIO.setup(STEP_PUMP, GPIO.OUT)
GPIO.setup(PUMP_IN, GPIO.OUT)

CAM_TRIGGER = 14
CAM_ECHO = 15
WATER_TRIGGER = 5
WATER_ECHO = 11
TOP_TRIGGER = 18
TOP_ECHO = 23
PUMP_TRIGGER = 24
PUMP_ECHO = 25
delay = 0.001
topHC = HCSR04(TOP_TRIGGER, TOP_ECHO)
camHC = HCSR04(CAM_TRIGGER, CAM_ECHO)
pumpHC = HCSR04(PUMP_TRIGGER, PUMP_ECHO)
waterHC = HCSR04(WATER_TRIGGER, WATER_ECHO)
mpu = MPU6050()
mpu.begin()
mpu.calcOffset()
factory = PiGPIOFactory()
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
print("Caculating offset, do not move MPU6050")
sleep(1)
cl = Client()
hostUrl = "http://192.168.137.1:8000/"
cl.connect(hostUrl)
def pulse_generator():
	while True:
		GPIO.output(STEP, GPIO.HIGH)
		sleep(delay)
		GPIO.output(STEP, GPIO.LOW)
		sleep(delay)

def run_forward():
	GPIO.output(DIR, CW)
	pulse_generator()
	
def run_backward():
	GPIO.output(DIR, CCW)
	pulse_generator()


def run_pump(seconds):
	GPIO.output(PUMP_IN, GPIO.HIGH)
	sleep(seconds)
	GPIO.output(PUMP_IN, GPIO.LOW)

# start functions
def start_forward():
	stop_forward_cmd()
	servo.mid()
	global forward, pid
	forward = Process(target = run_forward)
	forward.start()
	with pid.get_lock():
		pid.value = forward.pid
	print("send pid", forward.pid)

def stop_forwarding(pid):
	if(pid.value > 0):
		os.kill(pid.value, signal.SIGTERM)	
		with pid.get_lock():
			pid.value = 0
	

def start_backward():
	servo.mid()
	global backward
	backward = Process(target = run_backward)
	backward.start()

# Stop functions

def stop_backward():
	if(backward.is_alive()):
		backward.terminate()
		backward.join()

def stop_forward_cmd():
	global stop, pid 
	stop = Process(target = stop_forwarding, args=(pid,))
	stop.start()
	sleep(0.2)
	stop.terminate()
	stop.join()


def stopAll():
	servo.value = 0
	GPIO.output(STEP,GPIO.LOW)
	stop_forward_cmd()
	stop_backward()

def armSlide(dirPin, stepPin,direction, pulses):
    GPIO.output(dirPin, direction)
    for x in range(0, pulses):
        GPIO.output(stepPin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(stepPin, GPIO.LOW)
        sleep(delay)
def autoPredict():
	requests.get(hostUrl + "predicting/status?auto=1")
def waterLevelUpdate(value):
	requests.get(hostUrl + f"waterLevel/update?value={value}")
def checkDirection(pid, diseaseCount):
	while True:
		if(camHC.get_distance() < 25):
			if(pid.value > 0):
				print("cam detect")
				stop_forward_cmd()
				autoPredict()
		if(pumpHC.get_distance() < 25):
			if(pid.value > 0):
				print("Pump Detect Obstacle")
				stop_forward_cmd()
				if(diseaseCount.value >0):
					run_pump(diseaseCount.value + 1)
					diseaseCount.value = 0
					waterLevelUpdate(18 -waterHC.get_distance())
				start_forward()
				
				# if(diseaseCount.value >= 1):
				# 	run_pump(diseaseCount.value + 1)
				# 	diseaseCount.value = 0
				# 	cl.emit("waterLevel",18 - waterHC.get_distance(), namespace="/")
				# 	start_forward()
		# turn left
		if(topHC.get_distance() < 20):
			print("Front obs detect")
			if(pid.value > 0):
				servo.value = 0.38
				sleep(3)
				servo.value = 0
			
			
		sleep(0.8)

if __name__ == "__main__":

	servo.value = 0
	pid = Value("i", 0)
	count = Value("i", 0)
	diseaseCount = Value("i", 0)
	pulseHeight = Value("i", 0) 
	autoCamPos = Value("i", 0)
	forward = Process(target = run_forward)
	backward = Process(target = run_backward)
	stop = Process(target = stop_forwarding, args = (pid, ))
	sensor = Process(target =checkDirection, args= (pid, diseaseCount) )
	sensor.start()
	@cl.on("control")
	def control(data):
		print(f"command from user {data}")
		
		if(data == "forward"):
			stop_backward()
			start_forward()
		if(data == "backward"):
			stop_forward_cmd()
			start_backward()
		if(data =="left"):
			servo.value = -0.38
		if(data == "right"):
			servo.value = 0.38
		if(data == "stop"):
			stopAll()
	@cl.on("camPos1")
	def camPosition(data):
		global autoCamPos
		autoCamPos.value = data['pos']
		armSlide(DIR_CAM, STEP_CAM, data['direct'], data['pulse'])
	@cl.on("pumpPos1")
	def pumpPosition(data):
		global pulseHeight
		pulseHeight.value = data['pos']
		armSlide(DIR_PUMP, STEP_PUMP, data['direct'], data['pulse'])
	# height implement
	@cl.on("height1")
	def heightInput(data):
		print(data, type(data))
		direct = 0
		global pulseHeight, autoCamPos
		data = int(data) - 10
		if(data < 0): 
			data = 0
		pulse =0
		pulse = pulseHeight.value - round(data/60*2500)
		if pulse < 0:
			direct = 0
		else: direct = 1	
		pulseHeight.value = round((data/60)*2500)
		armSlide(DIR_PUMP, STEP_PUMP, direct, abs(pulse))
		armSlide(DIR_CAM, STEP_CAM, 1, autoCamPos.value)
		autoCamPos.value = 0


	
	@cl.on("manualRasPredict")
	def rasPredict(data):
		print("Ras predicting")
		result = capture_and_predict()
		cl.emit("rasPredictResult", result["response"])
		if(result["count"] >0):
			run_pump(result["count"] + 1)
	
	@cl.on("autoRasPredict")
	def rasPredict(data):
		global count, pulseHeight, diseaseCount, autoCamPos
		print("Ras predicting")
		autoCamPos.value = 0
		# first
		if(count.value ==0):
			armSlide(DIR_CAM, STEP_CAM, count.value%2, round(pulseHeight.value/2))
			autoCamPos.value = round(pulseHeight.value/2)
			result = capture_and_predict()
			with diseaseCount.get_lock():
				diseaseCount.value += result["count"]
			cl.emit("rasPredictResult", result["response"])
			sleep(2)
		elif(count.value%2 == 0):
			result = capture_and_predict()
			cl.emit("rasPredictResult", result["response"])
			sleep(2)
			armSlide(DIR_CAM, STEP_CAM, count.value%2, round(pulseHeight.value/2))
			autoCamPos.value = round(pulseHeight.value/2)
			with diseaseCount.get_lock():
				diseaseCount.value += result["count"]
	
		
		# second
		if(count.value ==0):
			armSlide(DIR_CAM, STEP_CAM, count.value%2, round(pulseHeight.value))
			cl.emit("predictStatus", 1)
			autoCamPos.value = round(pulseHeight.value)
			result = capture_and_predict()
			cl.emit("rasPredictResult", result["response"])
			with diseaseCount.get_lock():
				diseaseCount.value += result["count"]
		elif(count.value %2 ==1): 
			cl.emit("predictStatus", 1)
			result = capture_and_predict()
			cl.emit("rasPredictResult", result["response"])
			armSlide(DIR_CAM, STEP_CAM, count.value%2, round(pulseHeight.value/2))
			autoCamPos.value = round(pulseHeight.value)
			with diseaseCount.get_lock():
				diseaseCount.value += result["count"]

		with count.get_lock():
			count.value += 1
		start_forward()
			
	@cl.on("runPump")
	def manualPump(data):
		run_pump(3)

	@cl.on("reset")
	def reset(data):
		global pulseHeight, autoCamPos
		if(data):
			armSlide(DIR_CAM, STEP_CAM, 1, abs(autoCamPos.value))
			armSlide(DIR_PUMP, STEP_PUMP, 1, abs(pulseHeight.value))
			pulseHeight.value = 0	
			autoCamPos.value = 0	
	cl.emit("rasConnect",1, namespace="/")
	cl.emit("waterLevel",18 - waterHC.get_distance(), namespace="/")
	sensor.join()

