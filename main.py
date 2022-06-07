# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 20:45:06 2022

@author: Rodrigo
"""

#LIBRERIAS Y TEMA
from io import BytesIO
import menu_cliente
import menu_usuario
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
import sqlite3 as sq
from PIL import Image
import string
import nltk
import hashlib as hs
import altair_viewer
import base64
import jinja2
from geopy.distance import distance
import mysql.connector

#Conexion a BBDD
cnx = mysql.connector.connect(user='root',password='Pa1792007ra',
                              host='localhost',database='tuppershare')
#Estilo y colores para graficos de Streamlit
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
sns.set_style('whitegrid')
sns.set_context('talk')
tuppershare_color = ['#93C47D','#AE7DC4','#599B3C','#C47D92','#93C47D']
colortfm = sns.set_palette(sns.color_palette(tuppershare_color))



############################################################################
#funciones
def callback():
    st.session_state.boton=True
###########################################################################

def menu_usuarios(opcion,user):
    st.title(opcion)
    
#############################################MENU ADMIN

    if opcion=='Reporteria mensual':
        col1,col2,col3 = st.columns(3)
        #Graficos
        
############################################

    if opcion=='Recibir Tupperware':
        st.write('Seleccione los ID de los tupperware que quiere recibir:')
        #Tabla con los tupperware en estado fuera
        #Multiselect para colocar varios IDs
        #Boton para confirmar
        #Consultas para actualizar estado de tuppers a recibidos/almacenados
        #Actualizar tambien la ubicacion actual (de fuera al id del punto de recoleccion)
        #Actualizar IDPedido del ID a NULL
        st.multiselect('ID', [1,2,3,4,5])
        
############################################

    if opcion=='Enviar Tupperwares':
        st.write('Seleccione los Tupperware a enviar')
        #Tabla con los Tupper disponibles
        #Multiselect de los IDs
        #Actualizar la tabla de Tupper para cambiar estatus y columna ID
        
############################################

    if opcion=='Solicitudes de clientes':
        st.write('Lista de pedidos')
        #Mostrar tablas con ordenes de pedidos separadas por estatus
        
############################################

    if opcion=='Control de Tupperwares':
        st.write('Estatus de Tupperwares')
        #Mostrar tabla con los tupperwares y los estatus de cada uno
        
############################################

    if opcion=='Actualizar Estatus del pedido':
        st.write('Seleccione un pedido a actualizar')
        #Mostrar los pedidos
        #Seleccion multiple
        #Seleccionar el estatus al que se quiere actualizar
        #Boton de confirmar
        #Consulta de actualizacion de estatus de orden
        
############################################

    if opcion=='Ingresar Cliente':
        st.write('Ingrese los datos de los clientes')
        #Campos para insertar datos
        #Boton de actualizar
        #Consulta de insertar fila
        
############################################

    if opcion=='Editar/Remover Cliente':
        st.write('Seleccione un cliente')
        #Tabla con los clientes (no todos los campos)
        #Filtro por nombre,correo,telefono
        #Seleccionar varios ID
        #Boton de editar o remover
        #En editar:
            #Campos para cambiar datos
            #Boton de confirmar
            #Consulta para actualizar
        #En remover:
            #Boton de remover
            #Actualizar estatus
        
        
############################################MENU CLIENTE
        
    
    if opcion=='Reporteria':
        st.write('Graficos')
        
############################################

    if opcion=='Pedir Tupperware':
        if 'boton' not in st.session_state:
            st.session_state.boton=False
        #Pedir #Tuppers y de que tipo (depende de tipo de suscripcion de cliente)
        tupper1 = st.text_input('Cant. Tupperwares 1:',key=1)
        tupper2 = 0
        tupper3 = 0
        if int(user['tipoSuscripcion'])>1:
            tupper2 = st.text_input('Cant. Tupperwares 2:',key=2)
        if int(user['tipoSuscripcion'])>2:
            tupper3 = st.text_input('Cant. Tupperwares 3:',key=3)
        #if tupper1!='' and tupper2!='' and tupper3!='':
            #try:
             #   tupper1=int(tupper1)
              #  tupper2=int(tupper2)
               # tupper3=int(tupper3)
            #except:
             #   st.error('Datos mal ingresados')
        #Dataframe con usuario, cantidad de tuppers restantes de suscripcion y ubicacion
        if (st.button('Verificar disponibilidad',on_click=callback) or st.session_state.boton==True):
            st.write('Hay disponibles')
            Marker1 = [float(user['lat']),float(user['lon'])]
            locales = pd.read_sql('select lat,lon from Almacen;', cnx)
            distancias=[]
            #iconRest = folium.features.CustomIcon('restaurante.png',icon_size=(50,50))
            m = folium.Map(location=[41.38608229923676,2.1725463867187504], zoom_start=12)
            #Marker de restuarante
            folium.Marker(location=Marker1,tooltip='Mi restaurante',icon=folium.Icon(icon='cutlery',color="green")).add_to(m)
            #Markers de puestos de recoleccion
            for i in range(len(locales)):
                folium.Marker(location=(float(locales.iloc[i,0]),float(locales.iloc[i,1])),tooltip=f'Puesto {i}',popup=f'puesto{i}',
                              icon=folium.features.CustomIcon('tupper.png',icon_size=(50,50))).add_to(m)
                #Insertar distancias a dataframe
                distancias.append(distance(Marker1,(float(locales.iloc[i,0]),float(locales.iloc[i,1]))))
            #Graficar distancia minima
            folium.PolyLine((Marker1,(locales.loc[distancias.index(min(distancias)),'lat'],locales.loc[distancias.index(min(distancias)),'lon'])),tooltip=f'{min(distancias)}').add_to(m)
            #Obtener puesto con la cantidad de tupperwares solicitadas con el minimo de distancia
            
            #Graficar mapa
            output = st_folium(m, width=750, height=750)
            st.write(output)
            if st.button('confirmar pedido'):
                st.session_state.boton=False
                st.success('Pedido agregado crrectamente')
        #Guardar fecha actual para fecha_solicitud
        #Estatus: creada
        #Fecha_entrega=NULL
        
############################################

    if opcion=='Cancelar pedido':
        st.write('Seleccione un pedido')
        #Mostrar dataframe con los pedidos
        #Seleccionar ID
        #Mostrar datos del pedido
        #Boton para confirmar eliminar orden
        #Actualizar BBDD

############################################

    if opcion=='Metodos de pago':
        if 'boton' not in st.session_state:
            st.session_state.boton=False
            
        st.write('Su metodo de pago actual es:')
        query1_payment = f'SELECT * FROM metodoPago WHERE idCliente={user}'
        st.write(query1_payment)
        numTarjeta=0
        #Mostrar metodo actual
        st.write(f'Numero de tarjeta de debito:{numTarjeta}')
        #Indicar que se va a sobreescribir
        st.info('Si actualiza el metodo de pago, este se sobreescribirá')
        #Campo para numero de tarjeta
        if (st.button('Editar metodo de pago',on_click=callback) 
            or st.session_state.boton==True):
            numTarjeta=st.text_input('Numero de tarjeta')
            col1,col2 = st.columns(2)
            with col1:
                monthTarjeta = st.text_input('Mes')
            with col2:
                yearTarjeta = st.text_input('Anio')
            cvv = st.text_input('CVV',type='password')
            if st.button('Actualizar metodo de pago'):
                st.session_state.boton=False
                query2_payment = f'UPDATE metodoPago SET numeroTarjeta={numTarjeta},month={monthTarjeta},year={yearTarjeta},cvv={cvv} WHERE idCliente={user}'
                st.write(query2_payment)
                st.success('Metodo de pago actualizado')
                #Ejecutar consulta en base de datos con cursor o llamar API

############################################

    if opcion=='Sugerencias e inquietudes':
        st.write('Escribanos una sugerencia o pongase en contacto con nosotros')
        comment = st.text_area(label='Commentario')
        if st.button('Enviar comentario'):
            query1_comment = f'INSERT INTO Comentarios (idCliente,Comentario) VALUES({user},{comment})'
            st.write(query1_comment)
            #Ejecutar consulta en base de datos con cursor o llamar 
          
############################################
    
    if opcion=='Modificar datos':
        st.write('Mis Datos personales')
        query1_user = f'SELECT * FROM Cliente WHERE idCliente={user}'
        st.write(query1_user)
        nombre = st.text_input('Nombre','abc')
        correo = st.text_input('Correo','def')
        npassword = st.text_input('Contraseña',type='password',key='pass1')
        ntel = st.text_input('Telefono/Celular','ghi')
        if st.button('Actualizar datos'):
            st.success('Datos actualizados')
        
############################################

    if opcion=='Cancelar suscripción':
        if 'boton' not in st.session_state:
            st.session_state.boton=False
            
        st.write('¿Seguro que desea cancelar suscripción?')
        #Mostrar confirmacion
        st.info('Si cancela su suscripción, todavía tendrá acceso a nuestro servicio hasta la siguiente fecha de pago')
        #Boton de cancelar
        if (st.button('Cancelar suscripción',on_click=callback) or 
                     st.session_state.boton):
            st.error('¿Seguro que desea continuar?')
            if st.button('Si, cancelar mi suscripción'):
                query1_cancelarsus = f'UPDATE Cliente SET estatus=0 WHERE username={user}'
                st.write(query1_cancelarsus)
                st.session_state.boton=False
                st.success('Se ha dado de baja de nuestro servicio.')
                #Ejecutar consulta en base de datos con cursor o llamar API
        #Colocar un estatus "en cancelacion" que cambie hasta que el mes haya pasado
        
############################################

    if opcion=='Cambiar tipo de suscripcion':
        query1_sus = 'SELECT tipoSuscripcion FROM Cliente WHERE idCliente={username}'
        st.write(query1_sus)
        tipo_sus=1
        st.write('Suscripcion Actual: {tipo_sus}')
        suscripciones=['Seleccione el nuevo tipo de suscripcion',1,2,3]
        suscripciones.remove(tipo_sus)
        n_sus = st.selectbox('Seleccione el tipo de suscripcion',suscripciones)
        if n_sus != suscripciones[0]:
            if st.button('Cambiar suscripcion'):
                query2_sus = 'UPDATE Cliente SET tipoSuscripcion={n_sus} WHERE idCliente={user}'
                st.write(query2_sus)
                st.success('Suscripcion actualizada')
                st.info('Su plan cambiara desde el proximo dia de pago')
                #Ejecutar consulta en base de datos con cursor o llamar API
    
    return None

############################################################################

def main():
    #Lista con las opciones del selectbox del menu
    menu_admin = [
                'Reporteria mensual', #Tupperwares y metricas
                'Recibir Tupperware',
                'Enviar Tupperware',
                'Solicitudes de clientes',
                'Control de tupperwares',
                'Actualizar Estatus del pedido',
                'Ingresar Cliente',
                'Editar/Remover Cliente'
        ]
    
    menu_user = [
                'Reporteria',
                'Pedir Tupperware', #Utilizar mapas y distancias
                'Cancelar pedido',
                'Sugerencias e inquietudes',
                'Modificar datos',
                'Metodos de pago',
                'Cambiar tipo de suscripcion',
                'Cancelar suscripción'
        ]
    #Encabezado
    image = Image.open('icon.png')
    st.sidebar.image(image,width=200)
    st.sidebar.title("Tuppershare")
    #Opciones para la pantalla de inicio e ingreso
    menu1 = ["Inicio","Ingreso"]
    with st.sidebar:
        choice = option_menu(menu_title="Menu",
                         options=menu1,
                         icons=['arrow-up-circle','stack'])
    
    #Texto de inicio, cambiar Marco-View por nombre del programa
    if choice == "Inicio":
        st.write("# Bienvenido a Tuppershare")

	#Menu para ingresar usuario y contraseña
    if choice == "Ingreso":
        tipo_usuario = st.sidebar.selectbox('Tipo de usuario:',['usuario','cliente'])
        mail = st.sidebar.text_input("Usuario")
        password = st.sidebar.text_input("Contraseña",type='password')
        superuser = False
        if tipo_usuario=='usuario':
            user = pd.read_sql(f'select * from cliente where correo="{mail}";', cnx)
        else:
            user = pd.read_sql(f'select * from empleado where correo="{mail}";', cnx)
        token = 0
        st.write(f"Usuario: {mail}")
        if superuser:
            menu = menu_admin
        else:
            menu = menu_user
        a,mC,b = st.columns(3)
        opcion = mC.selectbox('Seleccione una opción',menu)
        menu_usuarios(opcion,user)

if __name__ == '__main__':
	main()