# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:47:16 2022

@author: Rodrigo
"""
from io import BytesIO
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from folium.plugins import Draw
import json
from collections import OrderedDict,defaultdict
import xlsxwriter
import streamlit as st
from databases import Database
import math
import pyotp
import sql
from sqlalchemy import create_engine
import pyodbc
import altair as alt
import numpy as pipnp
import pandas as pd
import seaborn as sns
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import datetime
from PIL import Image
import string
import nltk
import hashlib as hs
import altair_viewer
import base64
import jinja2
from geopy.distance import distance
import mysql.connector
import datetime

def callback():
    st.session_state.boton=True
    
def callback_canclear():
    st.session_state.boton_cancelar=True
    
def callback_update_1():
    st.session_state.boton_modificar_datos=True

def menu(opcion,user,cnx):
    idUser = user.idUsuario[0]
    nombre_i = user.nombre[0]
    correo_i = user.correo[0]
    tel_i = user.nTelefono[0]
    suscripcion_i = user.tipoSuscripcion[0]
    cant_i = user.nTupper[0]
############################################MENU CLIENTE
    if opcion=='Reporteria':
        st.write('Graficos')
        
############################################

    if opcion=='Pedir Tupperware':
        st.write(f'Cantidad de Tuppers disponibles: {cant_i}')
        if 'boton' not in st.session_state:
            st.session_state.boton=True
        #Pedir #Tuppers y de que tipo (depende de tipo de suscripcion de cliente)
        #Se ingresa la cantidad de tuppers
        #Se verifica que la cantidad de tuppers no exceda la cantidad de tuppers de la suscripcion
        tupper1 = 0
        tupper2 = 0
        tupper3 = 0
        tupper1 = st.text_input('Cant. Tupperwares 1:',key=1)
        if int(user['tipoSuscripcion'])>1:
            tupper2 = st.text_input('Cant. Tupperwares 2:',key=2)
            tupper3 = st.text_input('Cant. Tupperwares 3:',key=3)
        try:
            tupper1=int(tupper1) if tupper1!='' else 0
            tupper2=int(tupper2) if tupper2!='' else 0
            tupper3=int(tupper3) if tupper3!='' else 0
            if tupper1+tupper2+tupper3>cant_i:
                st.error('Ha excedido la cantidad de tuppers de su suscripcion, pongase en contacto con nostros')
            else:
                if (st.button('Verificar disponibilidad',on_click=callback) or 
                    st.session_state.boton) and tupper1+tupper2+tupper3>0:
                    #Ubicacion del restaurante
                    Marker1 = [float(user['lat']),float(user['lon'])]
                    #Ubicaciones de almacen
                    locales = pd.read_sql('select idAlmacen,lat,lon from Almacen;', cnx)
                    #Inicializacion de lista con distancias
                    distancias=[]
                    #iconRest = folium.features.CustomIcon('restaurante.png',icon_size=(50,50))
                    m = folium.Map(location=[41.38608229923676,2.1725463867187504], zoom_start=12)
                    #Marker de restuarante
                    folium.Marker(location=Marker1,tooltip='Mi restaurante',icon=folium.Icon(icon='cutlery',color="green")).add_to(m)
                    #Markers de puestos de recoleccion
                    st.write("Su orden saldrá del siguiente almacén:")
                    for i in range(len(locales)):
                        folium.Marker(location=(float(locales.iloc[i,1]),float(locales.iloc[i,2])),tooltip=f'Puesto {i}',popup=f'puesto{i}',
                                      icon=folium.features.CustomIcon('tupper.png',icon_size=(50,50))).add_to(m)
                        #Insertar distancias a lista
                        distancias.append(distance(Marker1,(float(locales.iloc[i,1]),float(locales.iloc[i,2]))))
                    #Graficar distancia minima
                    folium.PolyLine((Marker1,(locales.loc[distancias.index(min(distancias)),'lat'],locales.loc[distancias.index(min(distancias)),'lon'])),tooltip=f'{min(distancias)}').add_to(m)
                    #Obtener puesto con la cantidad de tupperwares solicitadas con el minimo de distancia
                        
                    #Graficar mapa
                    folium_static(m, width=750, height=750)
                    if st.button('Confirmar Pedido',5):
                        cnx.connect().execute(f'INSERT INTO Orden (idUsuario,idAlmacen,fecha_hora_solicitud,estatus,fecha_hora_entrega,nTupper1,nTupper2,nTupper3) VALUES ("{idUser}",{locales.loc[distancias.index(min(distancias)),"idAlmacen"]},now(),"Pendiente de aprobar",NULL,{tupper1},{tupper2},{tupper3});')
                        cnx.connect().execute(f'UPDATE usuario SET nTupper=nTupper-{tupper1+tupper2+tupper3} WHERE idUsuario="{idUser}";')
                        cnx.connect().execute('commit;')
                        st.success('Pedido agregado crrectamente')
                        st.session_state.boton=False
        except:
            st.error('Datos mal ingresados')
        #Dataframe con usuario, cantidad de tuppers restantes de suscripcion y ubicacion
        
############################################

    if opcion=='Cancelar pedido':
        if 'boton_cancelar' not in st.session_state:
            st.session_state.boton_cancelar=False
        st.write('Seleccione un pedido')
        ordenes = pd.read_sql(f'select idOrden,estatus,nTupper1,nTupper2,nTupper3,nTupper1+nTupper2+nTupper3 total from orden where idUsuario="{idUser}" and estatus="Pendiente de Aprobar";', cnx)
        st.table(ordenes)
        ids = st.multiselect("Ordenes (ID)", ordenes['idOrden'])
        if (st.button('Cancelar pedidos',on_click=callback_canclear,key=6) or 
                     st.session_state.boton_cancelar):
            for orden in ids:
                cnx.connect().execute(f'update orden set estatus="Cancelado" where idOrden="{orden}";')
                cnx.connect().execute(f'update usuario set nTupper=nTupper+{int(ordenes.loc[ordenes["idOrden"]==orden,"total"])} where idUsuario="{idUser}";')
            cnx.connect().execute('commit;')
            st.success("Ordenes Canceladas")
            st.session_state.boton_cancelar=False

############################################

    if opcion=='Sugerencias e inquietudes':
        st.write('Escribanos una sugerencia o pongase en contacto con nosotros')
        comment = st.text_area(label='Commentario')
        if st.button('Enviar comentario',key=7):
            cnx.connect().execute(f'INSERT INTO Comentarios (idUsuario,Comentario,fecha_publicacion) VALUES("{idUser}","{comment}",now());')
            cnx.connect().execute('commit;')
            st.success("Comentario Enviado. Gracias por ponerse en contacto con nosotros")
          
############################################
    
    if opcion=='Modificar datos':
        if 'boton_modificar_datos' not in st.session_state:
            st.session_state.boton_modificar_datos=False
        st.write('Mis Datos personales')
        nombre_n = st.text_input('Nombre',nombre_i)
        correo_n = st.text_input('Correo',correo_i)
        tel_n = st.text_input('Telefono/Celular',tel_i)
        password_n1 = st.text_input('contrasenia',type='password',key='pass1')
        cambio_contrasenia=False
        if password_n1!='':
            password_n2 = st.text_input('Verifique contrasenia nueva',type='password',key='pass1')
            if password_n1 == password_n2:
                st.success("contrasenia verificada")
                cambio_contrasenia=True
        if nombre_n!=nombre_i or correo_n!=correo_i or tel_n!=tel_i:
            if (st.button('Actualizar datos',on_click=callback_update_1,key=8) 
                or st.session_state.boton_modificar_datos):
                pword = st.text_input("Ingrese contrasenia actual",type='password')
                if pword!='':
                    if (st.button("Confirmar cambios",key=9) and pword=='123'):
                        if cambio_contrasenia==True:
                            cnx.connect().execute(f'UPDATE usuario SET nombre="{nombre_n}",correo="{correo_n}",nTelefono="{tel_n}",contrasenia="{password_n1}" WHERE idUsuario="{idUser}"')
                            st.success('Datos actualizados 1')
                            st.session_state.boton_modificar_datos=False
                        if cambio_contrasenia==False:
                            cnx.connect().execute(f'UPDATE usuario SET nombre="{nombre_n}",correo="{correo_n}",nTelefono="{tel_n}" WHERE idUsuario="{idUser}"')
                            st.success('Datos actualizados 2')
                            st.session_state.boton_modificar_datos=False
                            #Ejecutar consulta en base de datos con crursor o llamar API
        
############################################

    if opcion=='Cancelar suscripción':
        if 'boton_baja' not in st.session_state:
            st.session_state.boton_baja=False
            
        st.write('¿Seguro que desea cancelar suscripción?')
        #Mostrar confirmacion
        st.info('Si cancela su suscripción, todavía tendrá acceso a nuestro servicio hasta la siguiente fecha de pago')
        #Boton de cancelar
        if (st.button('Cancelar suscripción',on_click=callback) or 
                     st.session_state.boton):
            st.error('¿Seguro que desea continuar?')
            if st.button('Si, cancelar mi suscripción',key=10):
                cnx.connect().execute(f'INSERT INTO suscripcionCliente(idUsuario,suscripcionAnterior,suscripcionNueva,fecha_actualizacion) VALUES("{idUser}","{suscripcion_i}","DE BAJA","{datetime.date.today()}")')
                cnx.connect().execute(f'update usuario set fechaBaja="{datetime.date.today()}" where idUsuario="{idUser}";')
                cnx.connect().execute('commit;')
                st.session_state.boton_baja=False
                st.success('Se ha dado de baja de nuestro servicio.')
                #Ejecutar consulta en base de datos con crursor o llamar API
        
############################################

    if opcion=='Cambiar tipo de suscripcion':
        st.write(f'Suscripcion Actual: {suscripcion_i}')
        suscripciones=['Seleccione el nuevo tipo de suscripcion',1,2]
        suscripciones.remove(suscripcion_i)
        if suscripcion_i==1:
            st.write("Descripcion 1")
        elif suscripcion_i==2:
            st.write("Suscripcion 2")
        suscripcion_n = st.selectbox('Seleccione el tipo de suscripcion',suscripciones)
        if suscripcion_n != suscripciones[0]:
            if st.button('Cambiar suscripcion',key=11):
                cnx.connect().execute(f'INSERT INTO suscripcionCliente(idUsuario,suscripcionAnterior,suscripcionNueva,fecha_actualizacion) VALUES("{idUser}","{suscripcion_i}","{suscripcion_n}","{datetime.date.today()}")')
                cnx.connect().execute(f'UPDATE usuario SET tipoSuscripcion={int(suscripcion_n)} WHERE idUsuario="{idUser}";')
                cnx.connect().execute('commit;')
                st.success('Suscripcion actualizada')
                st.info('Su plan cambiara desde el proximo dia de pago')
                #Ejecutar consulta en base de datos con cursor o llamar API
                
############################################

    if opcion=='Cerrar Sesion':
        st.title("Sesion Cerrada, vuelva pronto")
    return None