#!/usr/bin/env python3
# so that script can be run from Brickman
from ev3dev.ev3 import *
from time import sleep, perf_counter
import csv
import os.path
import array
 
robot_speed = -900
Kp = 1/25
max_left = 0
max_right = 0
Kd = 1/100

def left_align():
	steer_init = steer_motor.position
	print(steer_init)
	steer_curr = 0
	#max_left = 0;
	var =1
	
	while (var == 1):
		#print(var)
		steer_init = steer_motor.position
		steer_motor.run_to_rel_pos(position_sp=10,speed_sp=700)
		sleep(0.05)
		steer_curr = steer_motor.position
		diff_steer = steer_curr - steer_init
		if(diff_steer<5):
			max_left = steer_init
			break
	return max_left

def right_align():
	#max_right = 0
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
	steer_center = ((max_right-max_left)/2.0) + 1.5 #if left_align is called before right_align, the order needs to be reversed 
	print("Steer_Center", steer_center)
	steer_motor.run_to_rel_pos(position_sp=steer_center,speed_sp=700,stop_action='hold')


def adjust_for_vehicle_separation(infrared_sensor_value, motor_duty_cycle):
    modified_motor_speed = min(max((infrared_sensor_value-10)/60, 0), 1)*motor_duty_cycle
    return modified_motor_speed

def Steer(error, derivative):
	#Simple PD controller
	steering_angle = Kp*(error) + Kd*derivative
	#print("Steering Angle: ",steering_angle)
	#print("max left:", max_left)
	if(steering_angle>max_left):
		steering_angle = max_left
	if(steering_angle<max_right):
		steering_angle = max_right
	return steering_angle
	
#Connect  the steering motor	
steer_motor=MediumMotor('outB'); assert steer_motor.connected,"Connect the right motor to port B."
max_right = right_align()
max_left = left_align()
align_center(max_left, max_right)
print(steer_motor.position)
steer_motor.wait_while('running')
steer_motor.stop(stop_action='brake')

touch_sensor = TouchSensor() 
color_sensor_right=ColorSensor('in2')
color_sensor_right.mode='COL-REFLECT'
color_sensor_left = ColorSensor('in1')
color_sensor_left.mode='COL-REFLECT'
infrared_sensor=InfraredSensor('in3')

#Connects the motors 
#touch_sensor = TouchSensor()
left_motor=LargeMotor('outC'); assert left_motor.connected, "Connect the left motor to port A."
right_motor=LargeMotor('outA'); assert right_motor.connected, "Connect the right motor to port D."
motor_duty_cycle = robot_speed

last_error = 0
current_error = 0

StartTime=perf_counter()
previous_time=0
#previous_values = [current_error]*8
#past_times = [StartTime]*8              
#prev_index = 0
#count = 0

while not touch_sensor.value():
	motor_duty_cycle = robot_speed
	current_time=perf_counter()
	left_SVal = color_sensor_left.value() 
	right_SVal = color_sensor_right.value()
	#find the difference in steering values to see if on the line or not
	current_error = left_SVal - right_SVal
	
	#D Control with 3 readings in the past
	#prev_index = count%3
	#diff_error = current_error-previous_values[prev_index]
	#dt3 = current_time - past_times[prev_index]
	#derivative=diff_error/dt3
	
	#Simple D controller:
    #find the difference in time and then calculate change in error dE/dt
	diff_error = current_error - last_error
	dt=current_time-previous_time
	derivative = diff_error/dt
	
	ir_sensor_value=infrared_sensor.value()
	
	if(current_error>0):
		steer_angle = Steer(current_error,derivative)
		motor_duty_cycle=adjust_for_vehicle_separation(ir_sensor_value, motor_duty_cycle)
	elif(current_error<0):
		steer_angle = Steer(current_error, derivative)	
		motor_duty_cycle=adjust_for_vehicle_separation(ir_sensor_value, motor_duty_cycle)
	else:
		steer_angle = 0
		motor_duty_cycle=adjust_for_vehicle_separation(ir_sensor_value, motor_duty_cycle)
	
	steer_motor.run_to_rel_pos(position_sp=steer_angle,speed_sp=700)

	left_motor.run_forever(speed_sp=motor_duty_cycle)
	right_motor.run_forever(speed_sp=motor_duty_cycle)
	#sleep(0.01)
	last_error = current_error
	previous_time=current_time
	#count = count+1
	#steer_motor.stop(stop_action='brake')
left_motor.stop(stop_action='brake')
right_motor.stop(stop_action='brake')
TotalTravelTime=perf_counter()-StartTime
print('The total travel time for the robot was: ' + str(TotalTravelTime) + ' seconds')