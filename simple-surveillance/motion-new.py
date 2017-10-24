'''
Dependencias
	python 2.4+
	opencv 3.0+
	  numpy 
	imutils
'''

# pacotes necessarios
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2

# funcao do envio de emails
def SendMail(ImgFileName):
	fromaddr = "QUEM ENVIA"
	toaddr = "QUEM RECEBE"
 
	msg = MIMEMultipart()
 
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "TITULO DO EMAIL"
	
	body = "CORPO DA MSG"
	msg.attach(MIMEText(body, 'plain'))
	
	filename = ImgFileName
	attachment = open("motionPhoto.png", "rb")
	
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
	
	msg.attach(part)
	# inicializando servidor e enviando email
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "SUA SENHA")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
 
# construcao do argumento para minima area de deteccao
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())
 
# inicializa webcam
camera = cv2.VideoCapture(0)

# inicializa primeiro frame da captura do video
firstFrame = None

# inicializa contador do intervalo de deteccoes e texto de status
icount = 0
text = "Sem movimento"

# itera sobre os frames do video 
while True:
	#  inicializa o frame atual e inicaliza o texto de sem movimento/obj detectado
	(grabbed, frame) = camera.read()
	
	text = "Sem movimento"
 
	# se o frame atual nao for inicializado o processo acaba
	if not grabbed:
		break
 
	# altera tamanho do frame, converte para escala de cinza e suaviza o contraste
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
	# se o primeiro frame nao existir o mesmo e inicializado
	if firstFrame is None:
		firstFrame = gray
		continue

	# processa a diferenca absoluta entre o primeiro frame e o atual
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 30, 255, cv2.THRESH_BINARY)[1]
 
	# cria os limites do objeto e procura os contornos
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 
	# itera sobre os contornos
	for c in cnts:
		# se o contorno for menor que o valor minimo de deteccao, ignora
		if cv2.contourArea(c) < args["min_area"]:
			continue
		
		# cria uma caixa para o contorno, desenha no frame e atualiza o texto ds status
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (93, 28, 233), 2)
		text = "Objeto detectado"
		icount += 1

	# apenas um controle dos loopings
	if(text != "Sem movimento"):
		print(text + str(icount))
	

	# escreve a label de status e horario no frame
	cv2.putText(frame, "Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (195, 222, 71), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (195, 222, 71), 1)
 
	# mostra os camadas do processo 
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)

	# intervalo de detecoes e envio do alerta
	if(icount >= 100):
		cv2.imwrite('motionPhoto.png', frame)
		cv2.imshow('Detection', frame)
		#SendMail('motionPhoto.png')
		print('send email')
		icount = 0

	key = cv2.waitKey(1) & 0xFF
 
	# programa para quando a tecla 'q' e pressionada
	if key == ord("q"):
		break
 
# para a webcam e feha todas janelas abetas
camera.release()
cv2.destroyAllWindows()    