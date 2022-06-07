# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 19:36:08 2022

@author: Rodrigo
"""

#Crear QR
import qrcode
from PIL import Image
logo = Image.open('logo.png')
basewidth=75
wpercent = (basewidth/float(logo.size[0]))
hsize = int((float(logo.size[1])*float(wpercent)))
logo = logo.resize((basewidth,hsize), Image.ANTIALIAS)
img = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
img.add_data('https://www.tuppershare.com/')
img.make()
img = img.make_image(fill_color='green',back_color='white').convert("RGB")
pos = ((img.size[0]-logo.size[0])//2,(img.size[1]-logo.size[1])//2)
img.paste(logo,pos)
img.save('test.jpg')

#Decodificar QR
from pyzbar.pyzbar import decode
data = decode(Image.open('test.jpg'))
print(data[0][0])