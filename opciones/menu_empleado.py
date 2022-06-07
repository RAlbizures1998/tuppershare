# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 16:46:53 2022

@author: Rodrigo
"""
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import leafmap.foliumap as leafmap
from streamlit_option_menu import option_menu
from folium.plugins import Draw,MousePosition
import streamlit as st
import pyotp
from sqlalchemy import create_engine
import pyodbc
import altair as alt
import numpy as pipnp
import pandas as pd
import seaborn as sns
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from PIL import Image
import altair_viewer
import base64
import jinja2
from geopy.distance import distance
import datetime

############################################################################
#funciones
def callback():
    st.session_state.boton=True
###########################################################################

def menu(opcion,user,cnx):
    idUser = user.idUsuario[0]
    nombre_i = user.nombre[0]
    correo_i = user.correo[0]
    almacen_i = user.idAlmacen[0]
    st.title(opcion)
    
#############################################MENU ADMIN

    if opcion=='Reporteria mensual':
        col1,col2,col3 = st.columns(3)
        #Graficos
        
############################################
#Ejecutar consulta

    if opcion=='Recibir Tupperware':
        st.write('Seleccione los ID de los tupperware que quiere recibir:')
        tuppers_fuera = pd.read_sql('SELECT idTupper,tipo,idOrden FROM tupper where estatus="Fuera";', cnx)
        n1,n2 = st.columns(2)
        filtro_recibir1 = n1.selectbox("Tipo",["","1","2"])
        if filtro_recibir1 != "":
            tuppers_fuera = tuppers_fuera.loc[tuppers_fuera['tipo']==filtro_recibir1,:]
        filtro_recibir2 = n2.selectbox("Orden",[""]+list(set((tuppers_fuera['idOrden'].dropna()))))
        if filtro_recibir2 != "":
            tuppers_fuera = tuppers_fuera.loc[tuppers_fuera['idOrden']==filtro_recibir2,:]
        st.write(tuppers_fuera)
        lista_devueltos = st.multiselect('ID', tuppers_fuera.idTupper)
        if st.button("Recibir Tuppers",key=1):
            for i in lista_devueltos:
                #Ejecutar consultas / editar
                query_devueltos = f'UPDATE tupper SET estatus="En Almacen",idOrden=NULL,idAlmacen="{almacen_i}" WHERE idTupper={i}'
                st.write(query_devueltos)
                query_logTupperDevueltos = f'INSERT INTO tuppersdevueltos (idTupper,fecha_hora_devolucion,idAlmacen) VALUES ({i},NOW(),{almacen_i})'
                st.write(query_logTupperDevueltos)
            st.success("Los tuppers han sido recibidos en el almacen")
        
############################################
#Ejecutar consulta

    if opcion=='Enviar Tupperwares':
        st.write('Seleccione los Tupperware a enviar')
        #IDs Pedidos
        pedidos_salida = pd.read_sql('SELECT idOrden,idUsuario,estatus,idAlmacen,fecha_hora_solicitud FROM orden WHERE estatus="Pendiente de aprobar"',cnx)
        st.write(pedidos_salida)
        idorden_salida = st.selectbox("ID Orden",['']+list(pedidos_salida['idOrden']))
        
        #IDs Tuppers
        tuppers_salida = pd.read_sql(f'SELECT idTupper,tipo,idAlmacen FROM tupper WHERE estatus="En Almacen" and idAlmacen={almacen_i}',cnx)
        filtro_recibir1 = st.selectbox("Tipo",["","1","2"])
        if filtro_recibir1 != "":
            tuppers_salida = tuppers_salida.loc[tuppers_salida['tipo']==filtro_recibir1,:]
        st.write(tuppers_salida)
        lista_envio = st.multiselect('ID', tuppers_salida.idTupper)
        boton2 = st.button("Enviar Orden",key='asdfaf')
        if boton2:
            #Ejecutar consultas / editar
            query_envio1 = f'UPDATE orden SET estatus="Enviado" WHERE idOrden={idorden_salida}'
            cnx.connect().execute(query_envio1)
            for i in lista_envio:
                query_envio2 = f'UPDATE tupper SET estatus="Fuera",idAlmacen=NULL,idOrden="{idorden_salida}" WHERE idTupper="{i}"'
                cnx.connect().execute(query_envio2)
            st.success("Orden enviada")
        
############################################

    if opcion=='Solicitudes de clientes':
        n0,n1,n0 = st.columns([1,2,1])
        orders = pd.read_sql('select * from orden',cnx)
        with n1:
            #Mostrar tablas con ordenes de pedidos separadas por estatus
            st.markdown(f"## Ordenes pendientes de aprobar: {len(orders.loc[orders['estatus']=='Pendiente de entregar',:])}")
            st.write(orders.loc[orders['estatus']=='Pendiente de entregar',:])
            st.markdown(f"## Ordenes aprobadas: {len(orders.loc[orders['estatus']=='Aprobado',:])}")
            st.write(orders.loc[orders['estatus']=='Aprobado',:])
            st.markdown(f"## Ordenes enviadas: {len(orders.loc[orders['estatus']=='Enviado',:])}")
            st.write(orders.loc[orders['estatus']=='Enviado',:])
            st.markdown(f"## Ordenes entregadas: {len(orders.loc[orders['estatus']=='Entregado',:])}")
            st.write(orders.loc[orders['estatus']=='Entregado',:])
            st.markdown(f"## Ordenes canceladas: {len(orders.loc[orders['estatus']=='Cancelado',:])}")
            st.write(orders.loc[orders['estatus']=='Cancelado',:])
        
############################################

    if opcion=='Control de Tuppers':
        tuppers_almacen = pd.read_sql('select idTupper,estatus,tipo,idAlmacen from tupper where idAlmacen is not null',cnx)
        tuppers_fuera = pd.read_sql('select idTupper,estatus,tipo,idOrden from tupper where idOrden is not null',cnx)
        st.markdown(f'## Tuppers en alamcen: {len(tuppers_almacen)}')
        n1,n2 =st.columns(2)
        n0,n3,n0 = st.columns([1,2,1])
        with n1:
            #Mostrar tabla con los tupperwares y los estatus de cada uno
            st.write(f"Alamcen 1: {len(tuppers_almacen.loc[tuppers_almacen['idAlmacen']==1])}")
            st.write(tuppers_almacen.loc[tuppers_almacen['idAlmacen']==1])
        with n2:
            st.write(f"Alamcen 2: {len(tuppers_almacen.loc[tuppers_almacen['idAlmacen']==2])}")
            st.write(tuppers_almacen.loc[tuppers_almacen['idAlmacen']==2])
        with n3:
            st.markdown(f'## Tuppers fuera: {len(tuppers_fuera)}')
            st.write(tuppers_fuera.sort_values('idOrden'))
        
############################################

    if opcion=='Actualizar Estatus del pedido':
        st.write('Seleccione un pedido a actualizar')
        #Filtar por cliente, estatus, almacen
        pedidos = pd.read_sql('select * from orden',cnx)
        n1,n2,n3 = st.columns(3)
        clientes = ['Seleccione una opcion']+list(set(pedidos['idUsuario']))
        f_cliente = n1.selectbox('Cliente:',clientes)
        if f_cliente != 'Seleccione una opcion':
            pedidos=pedidos.loc[(pedidos['idUsuario']==f_cliente),:]
        f_estatus = n2.selectbox('Estatus:',['Seleccione una opcion','Pendiente de aprobar','Aprobado','Enviado','Entregado','Cancelado'])
        if f_estatus != 'Seleccione una opcion':
            pedidos=pedidos.loc[(pedidos['estatus']==f_estatus),:]
        f_almacen = n3.selectbox('almacen:',['Seleccione una opcion',1,2])
        if f_almacen != 'Seleccione una opcion':
            pedidos=pedidos.loc[(pedidos['idAlmacen']==int(f_almacen)),:]
        #Mostrar los pedidos
        st.write(pedidos)
        #Seleccion multiple de los pedidos
        ids = st.multiselect('Seleccione los pedidos para actualizar',list(pedidos['idOrden']))
        if ids != []:
            #Seleccionar el estatus al que se quiere actualizar
            estatus_final = st.selectbox('Nuevo Estatus de orden:',['Seleccione una opcion','Pendiente de aprobar','Aprobado','Enviado','Entregado','Cancelado'])
            if estatus_final!='Seleccione una opcion':
                #Boton de confirmar
                if st.button('Actualizar estatus',3):
                    #Consulta de actualizacion de estatus de orden
                    for i in ids:
                        cnx.connect().execute(f'update orden set estatus="{estatus_final}" where idOrden={int(i)}')
                    st.success('Estatus acutalizado')
        
############################################

    if opcion=='Ingresar Nuevo Cliente':
        st.write('Ingrese los datos del nuevo cliente')
        n1,n2 = st.columns(2)
        with n1:
            #Campos para insertar datos
            nombre = st.text_input("Nombre de Cliente:")
            correo = st.text_input("Correo Electronico:")
            contrasenia = st.text_input("contrasenia:",type='password')
            telefono = st.text_input("Telefono:")
            tipoSuscripcion = st.selectbox('Tipo de suscripcion',['Seleccione una opcion',1,2])
            nTupper = 100 if tipoSuscripcion==1 else 200
        with n2:
            #Plottear Mapa y obtener coordenada
            m = leafmap.Map(location=[41.38608229923676,2.1725463867187504], zoom_start=12)
            #Graficar mapa
            mapa = st_folium(m, width=600, height=525)
        try:
            mapa = mapa['all_drawings'][0]['geometry']['coordinates']
            lat=mapa[1]
            lon=mapa[0]
            #Boton de actualizar
            if ((nombre!='') and (correo!='') and (contrasenia!='') and (telefono!='') and (tipoSuscripcion!='Seleccione una opcion')):
                if st.button("Ingresar cliente",4):
                    #Consulta de insertar fila
                    try:
                        cnx.connect().execute(f'insert into usuario(idUsuario,nombre,correo,contrasenia,nTelefono,estatus,idAlmacen,fechaAlta,tipoSuscripcion,nTupper,lat,lon,fechaBaja) values ("z1341","{nombre}","{correo}","{contrasenia}","{telefono}","Activo",NULL,"{datetime.date.today()}",{tipoSuscripcion},{nTupper},{lat},{lon},NULL);')
                        cnx.connect().execute('commit;')
                        st.success("Cliente ingresado correctamente")
                    except:
                        st.error("Usuario ya existente/Error de conexion")
        except:
            pass
        
############################################
#Ejecutar consulta

    if opcion=='Editar/Remover Cliente':
        st.write('Seleccione un cliente')
        #Tabla con los clientes (no todos los campos)
        clientes = pd.read_sql("select idUsuario,nombre,correo,nTelefono,estatus,fechaAlta,tipoSuscripcion from usuario where idAlmacen is null;",cnx)
        #Filtro por nombre,correo,telefono
        n1,n2 = st.columns(2)
        with n1:
            f_nombre = st.selectbox("Nombre cliente:",['']+list(set(clientes['nombre'])))
            if f_nombre!='':
                clientes = clientes.loc[clientes['nombre']==f_nombre,:]
            f_alta = st.selectbox("Fecha de alta",['']+list(set(clientes['fechaAlta'])))
            if f_alta!='':
                clientes = clientes.loc[clientes['fechaAlta']==f_alta,:]
        with n2:
            f_correo = st.selectbox("Correo electronico:",['']+list(clientes['correo']))
            if f_correo!='':
                clientes = clientes.loc[clientes['correo']==f_correo,:]
            f_tipo = st.selectbox("Tipo de suscripcion",['']+list(clientes['tipoSuscripcion']))
            if f_tipo!='':
                clientes = clientes.loc[clientes['tipoSuscripcion']==f_tipo,:]
        st.write(clientes)
        #Seleccionar varios ID
        ids = st.multiselect("IDs",list(clientes['idUsuario']))
        #Boton de editar o remover
        #En editar:
            #Campos para cambiar datos
            #Boton de confirmar
            #Consulta para actualizar
        #En remover:
            #Boton de remover
            #Actualizar estatus