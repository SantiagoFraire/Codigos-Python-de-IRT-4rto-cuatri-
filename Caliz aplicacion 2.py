# Librerias para Interfaz Grafica

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import *

#Librerias para expresiones regu. y conexion de dispositivos

import re
from netmiko import ConnectHandler

# Funcion para verificar formato de direccion fisica (MAC)

def type_format(Varia,sec):
    format_ = re.compile(sec)
    checar = format_.search(Varia)
    if checar == None:
        messagebox.showinfo(title = "Alerta", message = "Ingrese los datos respectivamente o verifique el formato de su direccion MAC")
        #Output.set("El tipo formato no es correcto, pruebe nuevamente.")
        return checar
    else:
        Output.set("La direccion MAC coincidio correctamente.")
        return checar.group()

# Funcion que se encarga de la busqueda de la MAC

def buscar_mac(mac,enlace):
    '''En esta seccion se empieza con la busqueda'''
    tab_mac = enlace.send_command(show_macTab + mac)
    '''En esta seccion, se obtiene la ubicacion del puerto
    por el cual, ve la mac nuestro SW'''
    format_ = re.compile(grupo_macTab)
    checar = format_.search(tab_mac)
    '''-------------------------------------------------------------------------------------------'''
    if checar != None:
        puerto = checar.group(1)
        #Output.set("La direccion MAC se encuentra en el puerto :",puerto)
        
    else:
        messagebox.showinfo(title = "Alerta", message = "No se encontro la direccion en la red.")
        #Output.set("No se encontro la direccion en la red.")
        return None
    '''--------------------------------------------------------------------------------------------'''
    '''En esta seccion, se le envia el 'cdp neighbors' para obtener
    informcion de los vecinos del SW'''
    det_cdp = enlace.send_command(show_cdpn_deT)
    #list_det_cdp = det_cdp.split('\n')

    ipsmore = re.findall(ips_more, det_cdp)
    print(ipsmore)

    ips = []
    [ips.append(i) for i in ipsmore if i not in ips]
    print(ips)

    inters = re.findall(inter_s, det_cdp)
    print(inters)
   
    i=0
    for secc_ip in inters:     
        format_ = re.compile(format_inter)
        checar = format_.search(secc_ip)
        inters[i] = checar.group(1) + checar.group(2)
        i+=1

    print(inters)
    
    if puerto in inters:
        pot = inters.index(puerto)
        ip = ips[pot]

        deviceSW = {
            "host":ip,
            "username":"cisco",
            "device_type":"cisco_ios",
            "secret":"cisco",
            "password":"cisco",
            }
        try:
            connect = ConnectHandler(**deviceSW)
            connect.enable()
        except:
            messagebox.showinfo(title = "Alerta", message = "Hubo un error de conexion.")
            return None
        
        
        buscar_mac(mac, connect)
        #connect.disconnect()
    else:
        host = enlace.send_command(show_host)
        format_ = re.compile(host_info)
        checar = format_.search(host)
        Output.set("La direccion de nuestro host esta en "+ checar.group(1) +", en su puerto " + puerto)
        #connect_enla.disconnect()
        #connect.disconnect()
        return None
        
# Conexion y Funcion inicial

'''En esta seccion, se declara una funcion, la cual estara enlazada a nuestro
boton 'Encontrar host', al presionarse dicho boton, se ejecutaran las
declaraciones siguientes dentro de esta funcion'''
def busca_host():
    
    while True:
        ip = IPswitch.get()
        user = UserName.get()
        password = Contraseña.get()
        mac = Direc_Mac.get()

        mac=mac.lower()
        
        Search_Mac = type_format(mac,mac_sec)
        
        '''Aqui le brindamos un formato convertido a cisco, a la MAC
        que ingresemos'''
        if Search_Mac != None:
            Search_Mac = Search_Mac.replace("-","")
            Search_Mac = Search_Mac.replace(".","")
            Search_Mac = Search_Mac.replace(":","")
            Search_Mac = list(Search_Mac)
            Search_Mac.insert(4,".")
            Search_Mac.insert(9,".")
            Search_Mac = "".join(Search_Mac)
            
            try:
                deviceSW = {
                    "host":ip,
                    "username":user,
                    "device_type":"cisco_ios",
                    "secret":password,
                    "password":password,
                    }
                connect_enla = ConnectHandler(**deviceSW)
                connect_enla.enable()
                print("Conectado")
                Output.set("Conexion establecida con el dispositivo.")
            except:
                #messagebox.showinfo(title = "Alerta", message = "Hubo un error de conexion, verifique sus datos")
                Output.set("Hubo un error de conexion, verifique sus datos.")
                break

            '''Aqui invocamos nuentra funcion 'buscar_mac'
            de manera inicial'''
            terminacion = buscar_mac(Search_Mac, connect_enla)
            if terminacion == None:
                break

        else:
            break

pestaña_emergente = messagebox.showinfo

def emergente():
    pestaña_emergente(title = "Instrucciones", message = "Inserte en sus repectivos recuadros la IP de su SW, el USUARIO y CONTRASEÑA configurada en su dispositivo principal, y la dirreccion fisica (MAC) del host que desea encontrar. Una vez hecho eso, presione 'Encontrar host'")

# Variables de secuencias y formatos representadas en expre. regu.

host_info = r"hostname (.*)"
format_inter = r"(Fa|Gi)[a-zA-Z]*([0-9]+\/[0-9]+\/?[0-9?]+)"
ips_more = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
inter_s = r"Interface:\s+[a-zA-Z]*\d+\/\d+\/?\d+"
ip_sec = r"\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}"
mac_sec = r"[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}"
grupo_macTab=r"\s*?\d\s+[a-f0-9]{4}\.[a-f0-9]{4}\.[a-f0-9]{4}\s+\w+\s+((Fa|Gi)\d{1,2}\/\d{1,2}\/?(\d{1,2})?)"
local_port = r"Interface:\s*(.*),(.*):\s*(.*)"

# Variables para ingresar comandos necesarios en los dispositivos.

show_macTab = "show mac address-table | in "
show_cdpn_deT = "show cdp neighbors detail"
show_host = "show running-config | include hostname"

# Apartado de Interfaz Grafica.

pestaña = tk.Tk()
pestaña.title("Aplicacion de busqueda")
imagen_fondo = tk.PhotoImage(file="C:\\Users\\alexa\\OneDrive\\Escritorio\\Traba. y Tareas 4rto (recu)\\Conmu. y Enru. de Redes (Eliud)\\opcion_fondo2.png")
imag_fondo = tk.Label(pestaña, image = imagen_fondo).place(x = 0,y= 0, relwidth = 1, relheight = 1)
pestaña.geometry("760x600+300+40")
pestaña.configure(bg = "#42B1E9")
pestaña.iconbitmap("Logo_api.ico")

'''Menubar'''

menubar = tk.Menu(pestaña)
pestaña.config(menu = menubar)
helpmenu = Menu(menubar, tearoff = 0)
helpmenu.add_command(label = "Instrucciones", command = emergente)
helpmenu.add_separator()
helpmenu.add_command(label = "Salir", command = pestaña.destroy)
menubar.add_cascade(label = "Ayuda", menu = helpmenu)

titles_col = "#42B1E9"
tipo_textos = ("Century Gothic",17)
tipo_titles = ("Century Gothic",15)
letra_titles_col = "#FCFEFF"

title = tk.Label(pestaña, text = "Busqueda de host en la red", font = ("Century Gothic",20), foreground = letra_titles_col, bg = titles_col)
title.place(x = 190, y = 10)

titleIP = tk.Label(pestaña, text = "Ingrese la direccion IP de tu SW:", font = tipo_titles, foreground = letra_titles_col, bg = titles_col)
titleIP.place(x = 30, y = 140)

titleU = tk.Label(pestaña, text = "Ingrese el Usuario:", font = tipo_titles, foreground = letra_titles_col, bg = titles_col)
titleU.place(x = 465, y = 140)

titleC = tk.Label(pestaña, text = "Ingrese la Contraseña:", font = tipo_titles, foreground = letra_titles_col, bg = titles_col)
titleC.place(x = 465, y = 270)

titleM = tk.Label(pestaña, text = "Ingrese la MAC del host:", font = tipo_titles, foreground = letra_titles_col, bg = titles_col)
titleM.place(x = 30, y = 270)

titleO = tk.Label(pestaña, text = "Ubicacion del host:", font = tipo_titles, foreground = letra_titles_col, bg = titles_col)
titleO.place(x = 288, y = 440)

btnM = tk.Button(pestaña, text = "Encontrar host", bg = "old lace", command = busca_host)
btnM.config(width = 15, height = 1, font = ("Century Gothic",11), activebackground = "#42B1E9", bg = "#DDE1E3")
btnM.place(x = 308, y = 365)

IPswitch = tk.StringVar()
IPsw = tk.Entry(pestaña, textvariable = IPswitch)
IPsw.place(x = 30, y = 170)
IPsw.config(width = 20, justify = "left", state = "normal", font = tipo_textos)

UserName = tk.StringVar()
User = tk.Entry(pestaña, textvariable = UserName)
User.place(x = 465, y = 170)
User.config(width = 20, justify = "left", state = "normal", font = tipo_textos)

Contraseña = tk.StringVar()
Contra = tk.Entry(pestaña, textvariable = Contraseña, show = '*')
Contra.place(x = 465, y = 300)
Contra.config(width = 20, justify = "left", state = "normal", font = tipo_textos)

Direc_Mac = tk.StringVar()
Mac = tk.Entry(pestaña, textvariable = Direc_Mac)
Mac.place(x = 30, y = 300)
Mac.config(width = 20, justify = "left", state = "normal", font = tipo_textos)

Output = tk.StringVar()
Out = tk.Entry(pestaña, textvariable = Output)
Out.place(x = 52, y = 470, height = 60)
Out.config(width = 54, justify = "left", state = "normal", font = ("Century Gothic",16))

pestaña.mainloop()

