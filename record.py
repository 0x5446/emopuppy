#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import os
import subprocess

# 设置GPIO模式
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 定义引脚
BUTTON_A = 17
BUTTON_B = 27
LED = 22

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
audio_file = os.path.join(script_dir, 'user_alert.wav')

# 设置引脚为输入和输出
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT)

recording = False
record_process = None

def cmd(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def start_recording():
    global recording, record_process
    if not recording:
        cmd("sudo systemctl stop emopuppy_monitor")
        record_process = subprocess.Popen([
            "arecord",
            "-D", "plughw:2,0",
            "-f", "cd",
            "-t", "wav",
            "-q",
            "-B", "1000000",
            "-F", "100000",
            audio_file
        ])
        GPIO.output(LED, GPIO.HIGH)
        recording = True
        print("Recording started...")

def stop_recording(save):
    global recording, record_process
    if recording:
        record_process.terminate()
        GPIO.output(LED, GPIO.LOW)
        recording = False
        if save:
            print("Recording saved.")
            for _ in range(2):
                GPIO.output(LED, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED, GPIO.LOW)
                time.sleep(0.1)
        else:
            clear_recording()

    cmd("sudo systemctl start emopuppy_monitor")

def clear_recording():
    if os.path.exists(audio_file):
        os.remove(audio_file)
        print("Recording canceled.")
        for _ in range(2):
            GPIO.output(LED, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(LED, GPIO.LOW)
            time.sleep(0.1)

try:
    while True:
        button_a_state = GPIO.input(BUTTON_A)
        button_b_state = GPIO.input(BUTTON_B)

        if button_a_state == GPIO.LOW and not recording:
            start_recording()
        
        if button_a_state == GPIO.HIGH and recording:
            stop_recording(save=True)

        if button_b_state == GPIO.LOW and not recording:
            clear_recording()

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()

