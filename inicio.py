# -*- coding: utf-8 -*-
"""
Created on Tue May 10 15:59:50 2022

@author: Rodrigo
"""

#LIBRERIAS Y TEMA
from io import BytesIO #
from opciones import menu_cliente,menu_empleado #
from streamlit_folium import folium_static,st_folium #
from streamlit_option_menu import option_menu  #
import json #
import streamlit as st #
import pyotp #
from sqlalchemy import create_engine #
import pyodbc #
import altair as alt #
import numpy as np #
import pandas as pd #
import seaborn as sns #
import psycopg2 #
import datetime #
import sqlite3 as sq #
from PIL import Image #
import string #
import hashlib as hs #
import base64 #
import jinja2 #

#Conexion a BBDD
cnx = create_engine('mysql://bed8d38ddc3df5:48fbd247@us-cdbr-east-05.cleardb.net/heroku_8d958cfdc32d7b3',echo=False)
#Estilo y colores para graficos de Streamlit
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
sns.set_style('whitegrid')
sns.set_context('talk')
tuppershare_color = ['#93C47D','#AE7DC4','#599B3C','#C47D92','#93C47D']
colortfm = sns.set_palette(sns.color_palette(tuppershare_color))


def main():
    #Lista con las opciones del selectbox del menu
    menu_admin = [
                'Reporteria mensual', #Tupperwares y metricas
                'Recibir Tupperware',
                'Enviar Tupperwares',
                'Solicitudes de clientes',
                'Control de Tuppers',
                'Actualizar Estatus del pedido',
                'Ingresar Nuevo Cliente',
                'Editar/Remover Cliente',
                'Cerrar sesión'
        ]
    
    menu_user = [
                'Reporteria',
                'Pedir Tupperware', #Utilizar mapas y distancias
                'Cancelar pedido',
                'Sugerencias e inquietudes',
                'Modificar datos',
                'Cambiar tipo de suscripcion',
                'Cancelar suscripción',
                'Cerrar sesión'
        ]
    menu1 = ["Inicio","Ingreso","Nuestros sitios de devolución"]
    #Encabezado
    image = Image.open('icon.png')
    st.sidebar.image(image,width=200)
    st.sidebar.title("Tuppershare")
    #Opciones para la pantalla de inicio e ingreso
    with st.sidebar:
        choice = option_menu(menu_title="Menu",
                             options=menu1,
                             icons=['arrow-up-circle','box-arrow-in-up','geo-alt'])
    
    #Texto de inicio, cambiar Marco-View por nombre del programa
    if choice == "Inicio":
        n0,n1,n2 = st.columns(3)
        with n1:
            st.write("# Bienvenido a Tuppershare")
            image = Image.open('icon.png')
            st.image(image,width=300)

	#Menu para ingresar usuario y contraseña
    if choice == "Ingreso":
        mail = st.sidebar.text_input("Usuario")
        password = st.sidebar.text_input("Contraseña",type='password')
        user=''
        if not(mail=='' or password==''):
            user = pd.read_sql(f'select * from usuario where correo="{mail}" and contraseña="{password}";', cnx)
        a,mC,b = st.columns(3)
        if type(user)!=str: 
            if user.empty:
                st.error("Correo y/o contraseña incorrecta")
            elif user['idUsuario'][0][0]=='E':
                opcion = mC.selectbox('Seleccione una opción',menu_admin)
                menu_empleado.menu(opcion,user,cnx)
            elif user['idUsuario'][0][0]=='C':
                opcion = mC.selectbox('Seleccione una opción',menu_user)
                menu_cliente.menu(opcion,user,cnx)
    if choice == "Nuestros sitios de devolución":
        st.title("Mapa")


if __name__ == '__main__':
	main()