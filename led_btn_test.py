from gpiozero import LED, PWMLED, Button
from signal import pause

red = PWMLED(26)
yellow = PWMLED(19)
btn_red = Button(16)
btn_yellow = Button(23)

while True:
	if btn_red.is_pressed:
		red.on()
	else:
		red.off()
	if btn_yellow.is_pressed:
		yellow.on()
	else:
		yellow.off()
