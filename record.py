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
audio_file = script_dir + '/user_alert.wav'

# 设置引脚为输入和输出
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT)

recording = False
record_process = None

def start_recording():
    global recording, record_process
    if not recording:
        # 使用 subprocess.Popen 启动 arecord 进程
        record_process = subprocess.Popen([
            "arecord",
            "-D", "plughw:2,0",
            "-f", "cd",
            "-t", "wav",
            "-q",
            "-B", "1000000", # 设置缓冲区大小为1秒
            "-F", "100000",  # 设置帧大小为0.1秒
            audio_file
            ])
        GPIO.output(LED, GPIO.HIGH)
        recording = True
        print("Recording started...")

def stop_recording(save):
    global recording, record_process
    if recording:
        # 使用 terminate 方法终止录音进程
        record_process.terminate()
        GPIO.output(LED, GPIO.LOW)
        recording = False
        if save:
            print("Recording saved.")
            # 闪烁 LED 两次表示保存成功
            for _ in range(2):
                GPIO.output(LED, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED, GPIO.LOW)
                time.sleep(0.1)
        else:
            # 删除录音文件
            os.remove(audio_file)
            print("Recording canceled.")

try:
    while True:
        button_a_state = GPIO.input(BUTTON_A)
        button_b_state = GPIO.input(BUTTON_B)

        if button_a_state == GPIO.LOW:
            if not recording:
                start_recording()
            if button_b_state == GPIO.LOW:
                stop_recording(save=True)
        else:
            if recording:
                stop_recording(save=False)

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()

