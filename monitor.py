#!/usr/bin/python3
import sys
import json
import subprocess
import os

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
alert_audio_file = script_dir + '/alert.wav'
user_alert_audio_file = script_dir + '/user_alert.wav'

import pygame

def play_audio(filename):
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(filename)
    sound.play()
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)


def is_angry(data, prob=0.6):
    if len(data) == 0:
        return False

    for entry in data:
        labels = entry['labels']
        scores = entry['scores']
        for label, score in zip(labels, scores):
            if (label.endswith('/angry') or label.endswith('/disgusted')) and score >= prob:
                print('[DEBUG] ' + label + ' SCORE:', score)
                return True

    return False

def play_sound(file_path):
    subprocess.run(['aplay', file_path])

def process_input():
    win = 2
    times = 0
    last_angry = False
    for line in sys.stdin:
        try:
            data = json.loads(line)
            if is_angry(data):
                times = (times + 1 if last_angry else 1)
                if times >= win:
                    if os.path.exists(user_alert_audio_file):
                        play_audio(user_alert_audio_file)
                    else:
                        play_audio(alert_audio_file)
                    print('[DEBUG] Somebody is angry or disgusted :(')
                    times = 0
                last_angry = True
            #print('@@@@@@ times: ', times)
        except json.JSONDecodeError:
            print('Error decoding JSON.')

if __name__ == '__main__':
    process_input()
