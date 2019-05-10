#!/usr/bin/env python3
# so that script can be run from Brickman
from ev3dev.ev3 import *
from time import sleep

def left_align():
	steer_init = steer_motor.position
	print(steer_init)
	steer_curr = 0
	max_left = 0;
	var =1
	
	while (var == 1):
		#print(var)
		steer_init = steer_motor.position
		steer_motor.run_to_rel_pos(position_sp=10,speed_sp=700)
		sleep(0.05)
		steer_curr = steer_motor.position
		diff_steer = steer_curr - steer_init
		#print("Steer Initial: %s and steer_curr: %s and diff: %s\n", str(steer_init),str(steer_curr),str(diff_steer))
		if(diff_steer<5):
			max_left = steer_init
			break
	return max_left
def right_align():
	max_right = 0
	steer_init = steer_motor.position
	print(steer_init)
	steer_curr = 0
	var =1
	while (var == 1):
		#print(var)
		steer_init = steer_motor.position
		steer_motor.run_to_rel_pos(position_sp=-10,speed_sp=700)
		sleep(0.05)
		steer_curr = steer_motor.position
		diff_steer = steer_curr - steer_init
		if(diff_steer>-5):
			max_right = steer_init
			break
	return max_right

def align_center(max_left, max_right):
	steer_center = 0
	steer_center = (max_right-max_left)/2.0
	print("Steer_Center", steer_center)
	#steer_motor.run_to_rel_pos(position_sp=(-1*steer_center),speed_sp=400)
	steer_motor.run_to_rel_pos(position_sp=steer_center,speed_sp=700,stop_action='hold')
	#Sound.beep()

steer_motor=MediumMotor('outB'); assert steer_motor.connected,"Connect the right motor to port B."

max_right = right_align()
max_left = left_align()
align_center(max_left, max_right)
print(steer_motor.position)
steer_motor.wait_while('running')
steer_motor.stop(stop_action='brake')

