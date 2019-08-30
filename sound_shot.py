import RPi.GPIO as GPIO
import time
import wiringpi
import time
import os
import smtplib
import imghdr
from email.message import EmailMessage

channel_3 = 12

def send_email():
    msg = EmailMessage()
    msg['Subject'] = 'Camera capture'
    msg['From'] = "projeto.puc.bes@gmail.com"
    msg['To'] = "projeto.puc.bes@gmail.com"
    msg.preamble = 'Foto capturada'

    img_data = open("captura.jpg", 'rb').read()
    msg.add_attachment(img_data, maintype='image', subtype=imghdr.what(None, img_data))
    s=smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login("projeto.puc.bes@gmail.com", "pucbes@19")
    s.send_message(msg)

def servo (angulo):
	valor = 60 + (190*angulo)/180
	wiringpi.pwmWrite(18, int(valor))

# Nome dos pinos no modo 'GPIO'
wiringpi.wiringPiSetupGpio()

# Configura pino18 como saida PWM
wiringpi.pinMode(channel_3, wiringpi.GPIO.PWM_OUTPUT)

# configura temporizacao PWM
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

def reset():
	servo(90)

def virar_direita():
	servo(45)

def virar_esquerda():
	servo(135)

channel_1 = 17 # sensor 1
channel_2 = 22 # sensor 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel_1, GPIO.IN)
GPIO.setup(channel_2, GPIO.IN)
tempos_1 = []
tempos_2 = []


def callback_1(channel_1):
    tempos_1.append(int(round(time.time() * 1000000)))
    print("Sensor 1: " + str(int(round(time.time() * 1000000))))


def callback_2(channel_2):
    tempos_2.append(int(round(time.time() * 1000000)))
    print("Sensor 2: " + str(int(round(time.time() * 1000000))))


GPIO.add_event_detect(channel_1, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel_1, callback_1)

GPIO.add_event_detect(channel_2, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel_2, callback_2)

reset()

while True:
    tempo_atual = int(round(time.time() * 1000000))
    if tempos_1 and tempos_2:  # Se ambos os sensores detectaram o som
        if abs(tempos_1[-1] - tempos_2[-1]) < 100000:  # Se a diferença entre os tempos dos sensores for menor que 10ms
            if abs(tempos_1[-1] - tempo_atual) < 100000:  # Se o som foi detectado no loop atual
                if tempos_1[-1] - tempos_2[-1] < 0:
                    virar_direita()
                    time.sleep(0.1)
                    os.system("sudo fswebcam 640x480 captura.jpg")
                    send_email()
                    reset()
                else:
                    virar_esquerda()
                    time.sleep(0.1)
                    os.system("sudo fswebcam 640x480 captura.jpg")
                    send_email()
                    reset()
    time.sleep(0.1)

