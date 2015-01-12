#=============================================================#
#                                                             #
#    EL EXPRESO DEL DEPORTE                                   #
#    ExpUp - Image Uploader                                   #
#-------------------------------------------------------------#
#    Developed by: Luis Jose Lopez Miranda                    #
#    This software is licensed under the MIT License (Expat)  #
#                                                             #
#=============================================================#

# Import all necessary modules

#1 - Tkinter
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

#2 - OS File I/O
import os
from os import listdir
from os.path import isfile, join, exists

#3 - Image Manipulation
import PIL
from PIL import Image, ImageTk, ImageEnhance

#4 - MySQL Integration
import pymysql
import sys

#5 - Internet I/O
import urllib.request,io

#6 - Passlib Hasher
import passlib
from passlib.hash import phpass

#7 - Wordpress Integration
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts

#8 - Time
import time

#9 - Threading
import threading

#10 - Mimetypes
import mimetypes

#11 - Random
import random

#12 - SMTP for email integration
import smtplib

#### Defines

# Software Info
SOFTWARE_NAME = "ExpUp"
SOFTWARE_DESCRIPTION = "Procesador de imagenes para El Expreso del Deporte"
VERSION = "0.1b"
AUTHOR = "Luis Jose Lopez Miranda"
AUTHOR_LINK = ""
LAST_REV = "11 de enero, 2015"

# Links
MAIN_IMAGE = 'images/header_ES.png'
WP_URL = 'http://elexpresodeldeporte.com/xmlrpc.php'
TEMP_FOLDER_NAME = "_temp/"
ICON_URL = 'images/expup.ico'

# MySQL-WP Information
WP_MYSQL_HOST = "ele1313311223367.db.10815705.hostedresource.com"
WP_MYSQL_USER = "ele1313311223367"
WP_MYSQL_PASS = "Ardilla18!"
WP_MYSQL_DB = "ele1313311223367"

# MySQL-EXPUP Information
MYSQL_HOST = "elexpreso.db.10815705.hostedresource.com"
MYSQL_USER = "elexpreso"
MYSQL_PASS = "Ardilla18!"
MYSQL_DB = "elexpreso"

# Size
MAX_W = 720
MAX_H = 640

# Colors
MAIN_BG = "#FFFFFF"
S_BG = "#000000"
TITLE_BG = "#FFFFFF"
I_BG = "#FF3300"
I_TEXT = "#FF3300"
MAIN_TEXT = "#000000"
S_TEXT = "#FFFFFF"

# Spanish texts
MY_SQL_ERROR = "Error en la conexion MySQL"
MAKE_SURE_INTERNET = "Asegurese de estar conectado a internet"
FIRST_STEP = "Seleccione la carpeta con las fotos que desea subir"
SELECT_FOLDER = "Seleccionar carpeta"
LOG_IN_PLEASE = "Por favor ingrese sus datos"
LOG_IN_TITLE = "Ingreso de Usuario"
NO_FOLDER_SELECTED = "No se ha seleccionado una carpeta"
FILES_SELECTED = " imagenes seleccionadas!"
NO_FILES_SELECTED = "La carpeta no contiene imagenes validas"
PLEASE_SELECT_FOLDER = "Por favor seleccione una carpeta"
USERNAME = "Nombre de usuario: "
PASSWORD = "Contraseña: "
SUCCESSFUL_LOGIN = "Conexion exitosa"
UNSUCCESSFUL_LOGIN = "Conexion fallida"
S_LOGIN_DESC = "Puede proceder a utilizar el programa"
U_LOGIN_DESC = "Credenciales no validas. Vuelva a intentarlo"
USER_NOT_FOUND = "Usuario no encontrado en la base de datos"
USER = "Usuario:"
ADMIN = "Administrador"
COL = "Colaborador"
INV = "Invitado"
PREVIEW = "Foto de ejemplo"
CONNECTION_ERROR = "Error de conexion con internet"
SET_NAME = "Escriba el nombre de la actividad"
UPLOAD = "Subir fotos"
NO_NAME = "Necesita establecer un nombre de archivo"
RANK_NOT_ENOUGH = "Usted no tiene el rango necesario para subir fotos."
BASE_STATE = "Trabajando..."
UPLOADING = "Subiendo: "
PROCESSING = "Procesando: "
FINISHED = "Finalizado!"
MENU_SETTINGS = "Opciones"
MENU_OPTION_QUIT = "Salir"
SHUTDOWN_FINISH = "Apagar la computadora al finalizar"
WILL_SHUTDOWN = "La computadora se apagara automaticamente despues de subir las fotos.\nPresione Aceptar para continuar, o Cancelar para volver. "
WARNING = "Advertencia"
CREDITS_INFO = SOFTWARE_NAME + "\n" + SOFTWARE_DESCRIPTION + "- Version: " + VERSION + "\nDesarrollado y diseñado por: Luis Jose Lopez Miranda\nUltima revision: " + LAST_REV
CREDITS = "Creditos"
WISH_TO_QUIT = "¿Realmente desea salir?"
PROCESS_ONGOING = "Las fotos se estas subiendo. Si cierra el programa, el proceso se interrumpirá.\nPresione Aceptar para salir o Cancelar para continuar"


# Associative fetching / By: Ian Howson
def FetchOneAssoc(cursor) :
    data = cursor.fetchone()
    if data == None :
        return None
    desc = cursor.description

    dict = {}

    for (name, value) in zip(desc, data) :
        dict[name[0]] = value

    return dict

logged = False
dirname = ""
valid_dir = False
images = []
user = ""
real_name = ""
rank = ""
act_name = ""
can_upload = False
password_sec = ""
step = 0

# Create a window
root = tk.Tk()
root.title(SOFTWARE_NAME + " || Version: " + VERSION)
root.resizable(width=False, height=False)
root.configure(background=S_BG)
root.option_add('*tearOff', tk.FALSE)
root.wm_iconbitmap(ICON_URL)

def askIfQuit():
    if (step > 3):
        if messagebox.askokcancel(WISH_TO_QUIT, PROCESS_ONGOING):
            root.destroy()
            sys.exit()
    else:
        root.destroy()
        sys.exit()

def handler():
    t2=threading.Thread(target=askIfQuit)
    t2.start()

root.protocol("WM_DELETE_WINDOW", handler)

def showCredits():
    messagebox.showinfo(CREDITS, CREDITS_INFO, parent=root)

# Create the menubar
menubar = tk.Menu(root)
root['menu'] = menubar
menu_settings = tk.Menu(menubar)
menubar.add_cascade(menu=menu_settings, label=MENU_SETTINGS)
menubar.add_command(label=CREDITS, command=showCredits)
# Set the variable for shutdown
shutdown_on_finish = tk.BooleanVar()
menu_settings.add_checkbutton(label=SHUTDOWN_FINISH, variable=shutdown_on_finish, onvalue=True, offvalue=False)
shutdown_on_finish.set(False)
menu_settings.add_command(label=MENU_OPTION_QUIT, command=handler)

# Set additional elements on the main window
title = tk.Frame(root, bg=MAIN_BG, width=MAX_W)
header_img = tk.PhotoImage(file=MAIN_IMAGE)
header_label = tk.Label(title, bg = MAIN_BG, image = header_img).pack()
title.pack()
progress = tk.Frame(root, bg=I_BG, width=MAX_W)

#Test DB Connection
try:
    conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASS, db=MYSQL_DB)
    wp_conn = pymysql.connect(host=WP_MYSQL_HOST, user=WP_MYSQL_USER, passwd=WP_MYSQL_PASS, db=WP_MYSQL_DB)
except:
    messagebox.showinfo(MY_SQL_ERROR, MAKE_SURE_INTERNET, icon="warning", parent = root)
    root.quit()
    sys.exit()

login_w = tk.Toplevel(root, takefocus = True)
login_w.wm_iconbitmap(ICON_URL)
instruct = tk.Frame(root, width=MAX_W, bg = S_BG, padx=10)
preview = tk.Frame(root, width=MAX_W, bg = S_BG)
folder_label = tk.Label(instruct, fg = S_TEXT, text = NO_FOLDER_SELECTED, bg = S_BG)
images_layout = tk.Frame(root, width=MAX_W, bg = S_BG)
images_label = tk.Label(instruct, fg = S_TEXT, text = PLEASE_SELECT_FOLDER, bg = S_BG)
preview_canvas = tk.Canvas ( preview, width=MAX_W/2, height=MAX_H/2.5, bg = I_BG )
m_name = tk.StringVar()

def first_step():
    global step
    step = 1
    login_w.title(LOG_IN_TITLE)
    textologin = tk.Label(login_w, text=LOG_IN_PLEASE).pack()
    user_label = tk.Label(login_w, text=USERNAME).pack()
    username = tk.StringVar()
    name = tk.Entry(login_w, textvariable=username)
    name.pack()
    pass_label = tk.Label(login_w, text=PASSWORD).pack()
    password = tk.StringVar()
    pswd = tk.Entry(login_w, textvariable=password, show = '*')
    pswd.pack()
    name.focus_set()
    login_w.transient(root)
    login_w.grab_set()
    login_w.geometry('400x120')
    login = tk.Button(login_w, text="Login", command=lambda: verifyUser(username.get(), password.get()))
    login.pack()
    root.wait_window(login_w)

def secondStep():
    global step
    step = 2
    user_label = tk.Label(title, bg = MAIN_BG, fg = MAIN_TEXT, text=USER + " " + real_name + ", " + rank).pack()
    if (can_upload):
        label_instruct1 = tk.Label(instruct, text=FIRST_STEP, bg = S_BG, fg=I_TEXT).pack()
        folder_label.pack()
        select_folder.pack()
        instruct.pack()
    else:
        tk.Label(title, bg = I_BG, fg = S_TEXT, text=RANK_NOT_ENOUGH).pack()

def startProcess():
    t1=threading.Thread(target=processImages)
    t1.start()

upload_button = tk.Button(preview, text=UPLOAD, command=startProcess, bg = S_BG, fg = S_TEXT)

def thirdStep():
    global step, conn
    m_img = Image.open(join(dirname+"/", random.choice(images)))
    if (step < 3):
        tk.Label(preview, text=SET_NAME, fg=I_TEXT, bg=S_BG).pack()
        name_entry = tk.Entry(preview, textvariable=m_name, bg=MAIN_BG, width=50)
        name_entry.pack()
        preview_img = applyWatermark(m_img, getWatermark())
        preview_img.thumbnail((MAX_W/2, MAX_H/2), Image.ANTIALIAS)
        preview_label = tk.Label(preview, bg = S_BG, fg = I_TEXT, text=PREVIEW).pack()
        photo = ImageTk.PhotoImage(preview_img)
        pr_img = tk.Label(preview, image=photo)
        pr_img.image = photo
        preview_canvas.create_image(MAX_W/4,MAX_H/5, image = photo)
        preview_canvas.pack()
        upload_button.pack()
        preview.pack()
    else:
        preview_img = applyWatermark(m_img, getWatermark())
        preview_img.thumbnail((MAX_W/2, MAX_H/2), Image.ANTIALIAS)
        preview_label = tk.Label(preview, bg = S_BG, fg = I_TEXT, text=PREVIEW).update()
        photo = ImageTk.PhotoImage(preview_img)
        pr_img = tk.Label(preview, image=photo)
        pr_img.image = photo
        preview_canvas.delete("all")
        preview_canvas.create_image(MAX_W/4,MAX_H/5, image = photo)
        preview_canvas.update()
    step = 3

def getHeightStd():
    cur = conn.cursor()
    if (cur.execute("SELECT height FROM settings")):
        r = FetchOneAssoc(cur)
        cur.close()
        return (r["height"])
    else:
        messagebox.showinfo(UNSUCCESSFUL_LOGIN, USER_NOT_FOUND, icon="warning", parent=root)

def getWidthStd():
    cur = conn.cursor()
    if (cur.execute("SELECT width FROM settings")):
        r = FetchOneAssoc(cur)
        cur.close()
        return (r["width"])
    else:
        messagebox.showinfo(UNSUCCESSFUL_LOGIN, USER_NOT_FOUND, icon="warning", parent=root)

def getWatermarkURL():
    cur = conn.cursor()
    if (cur.execute("SELECT watermark FROM settings")):
        r = FetchOneAssoc(cur)
        cur.close()
        return (r["watermark"])
    else:
        messagebox.showinfo(UNSUCCESSFUL_LOGIN, USER_NOT_FOUND, icon="warning", parent=root)


def verifyUser(u, p):
    global user, real_name, rank, password_sec, wp_conn
#if (wp_conn):
    cur = wp_conn.cursor()
    if (cur.execute("SELECT * FROM wp_users WHERE user_login = '"+u+"'")):
        r = FetchOneAssoc(cur)
        cur.close()
        if (phpass.verify(p,(r["user_pass"]))):
            password_sec = p
            login_w.destroy()
            logged = True
            user = u
            real_name = r["display_name"]
            rank = getRank(r["ID"])
            secondStep()
        else:
            messagebox.showinfo(UNSUCCESSFUL_LOGIN, U_LOGIN_DESC, icon="warning", parent=root)
    else:
        messagebox.showinfo(UNSUCCESSFUL_LOGIN, MAKE_SURE_INTERNET, icon="warning", parent=root)
#else:
    #wp_conn = pymysql.connect(host=WP_MYSQL_HOST, user=WP_MYSQL_USER, passwd=WP_MYSQL_PASS, db=WP_MYSQL_DB)
    #verifyUser(u, p)

# List all current images
def list_images(folder):
    pictures = [ f for f in listdir(folder) if isfile(join(dirname,f)) and (f.endswith(".jpg") or f.endswith(".png")  or f.endswith(".JPG")  or f.endswith(".PNG")) ]
    return pictures

def updateFolderLabel(content):
    global folder_label
    folder_label.config(text=content)
    
def selectFolder():
    global dirname
    global folder_label
    global images
    dirname = filedialog.askdirectory(mustexist = True)
    if (dirname != ""):
        updateFolderLabel(dirname)
        images = list_images(dirname)
        if (isValidDir()):
            thirdStep()

select_folder = tk.Button(instruct, text=SELECT_FOLDER, command=selectFolder, bg = S_BG, fg = S_TEXT)

# Apply watermark, by hasanatkazmi - modified by Luis Jose Lopez Miranda
def applyWatermark(im, mark):
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    position = (im.size[0]-mark.size[0], im.size[1]-mark.size[1])
    layer.paste(mark, position)
    watermarked = Image.composite(layer, im, layer)
    return watermarked

def getExt(file):
    if(file.endswith(".jpg") or file.endswith(".JPG")):
        return ".jpg"
    else:
        return ".png"

def isValidDir():
    amount_of_images = str(len(images))
    images_label.pack()
    if (len(images) > 0):
        images_label.config(text = amount_of_images + FILES_SELECTED)
        return True
    else:
        images_label.config(text = NO_FILES_SELECTED)
        return False

def writeImage(img, name):
    if not os.path.exists(TEMP_FOLDER_NAME):
        os.makedirs(TEMP_FOLDER_NAME)
    img.save( join(TEMP_FOLDER_NAME, name))

def uploadImage(loc, name):
    client = Client(WP_URL, user, password_sec)
    with open(join(loc,name), "rb") as img:
        data = {
            'name': name,
            'bits': xmlrpc_client.Binary(img.read()),
            'type': 'image/jpeg',
        }
        response = client.call(media.UploadFile(data))
    os.remove(join(loc,name))

def processImages():
    global step
    act_name = m_name.get()
    if (shutdown_on_finish.get() == False):
        if (act_name != ""):
                upload_button['state'] = 'disabled'
                select_folder['state'] = 'disabled'
                step = 4
                mark = getWatermark()
                size = getWidthStd(), getHeightStd()
                i = 0
                upload_progress = ttk.Progressbar(progress, orient='horizontal', mode='indeterminate')
                upload_progress.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
                v = tk.StringVar()
                current_label = tk.Label(progress, textvariable=v, bg = I_BG)
                current_label.pack()
                v.set(BASE_STATE)
                progress.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
                upload_progress.start(50)
                for file in images:
                    full_name = act_name + "_" + str(i) + "_" + time.strftime("%d_%m_%Y") + getExt(file)
                    full_path = TEMP_FOLDER_NAME + full_name
                    v.set(PROCESSING + " " + full_name)
                    m_img = Image.open(join(dirname+"/", file))
                    img = applyWatermark(m_img, mark)
                    img.thumbnail(size, Image.ANTIALIAS)
                    writeImage(img, full_name)
                    v.set(UPLOADING + " " + full_name)
                    uploadImage(TEMP_FOLDER_NAME, full_name)
                    i += 1
                upload_progress.stop()
                upload_progress.destroy()
                v.set(FINISHED)
                end()
        else:
            messagebox.showinfo("Error", NO_NAME, icon="warning", parent=root)
    else:
        if messagebox.askokcancel(title=WARNING, message=WILL_SHUTDOWN, parent=root):
            if (act_name != ""):
                upload_button['state'] = 'disabled'
                select_folder['state'] = 'disabled'
                step = 4
                mark = getWatermark()
                size = getWidthStd(), getHeightStd()
                i = 0
                upload_progress = ttk.Progressbar(progress, orient='horizontal', mode='indeterminate')
                upload_progress.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
                v = tk.StringVar()
                current_label = tk.Label(progress, textvariable=v, bg = I_BG)
                current_label.pack()
                v.set(BASE_STATE)
                progress.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
                upload_progress.start(50)
                for file in images:
                    full_name = act_name + "_" + str(i) + "_" + time.strftime("%d_%m_%Y") + getExt(file)
                    full_path = TEMP_FOLDER_NAME + full_name
                    v.set(PROCESSING + " " + full_name)
                    m_img = Image.open(join(dirname+"/", file))
                    img = applyWatermark(m_img, mark)
                    img.thumbnail(size, Image.ANTIALIAS)
                    writeImage(img, full_name)
                    v.set(UPLOADING + " " + full_name)
                    uploadImage(TEMP_FOLDER_NAME, full_name)
                    i += 1
                upload_progress.stop()
                upload_progress.destroy()
                v.set(FINISHED)
                end()
   
def wpConnect(u,p):
    wp = Client(WP_SITE_URL, u, p)
    return wp

def getWatermark():
    try:
        path = io.BytesIO(urllib.request.urlopen(getWatermarkURL()).read())
        watermark = Image.open(path)
        return watermark
    except:
        messagebox.showinfo(CONNECTION_ERROR, MAKE_SURE_INTERNET, icon="warning", parent=root)
        

def getRank(ID):
    global can_upload
    m_id = str(ID)
    cur = wp_conn.cursor()
    if (cur.execute("SELECT meta_value FROM wp_usermeta WHERE user_id = '"+m_id+"' AND meta_key = 'wp_user_level'")):
        r = FetchOneAssoc(cur)
        cur.close()
        rank = int(r['meta_value'])
        if (rank >= 10):
            can_upload = True
            return ADMIN
        elif (rank > 1):
            can_upload = True
            return COL
        else:
            can_upload = False
            return INV
    else:
        print("Error")

def recordData(user, name, amount, rank):
    global conn
    cur = conn.cursor()
    if (cur.execute("INSERT INTO `logs` (user ,name ,amount ,rank ) VALUES ( '"+user+"',  '"+name+"', '"+amount+"', '"+rank+"' );")):
        cur.close()
        print (rank + " " + user + " ha subido "+amount+" fotos con el nombre: "+name+".")
    else:
        print("Error")

def getAdminEmail():
    cur = conn.cursor()
    if (cur.execute("SELECT email FROM settings")):
        r = FetchOneAssoc(cur)
        cur.close()
        return (r["email"])
    else:
        messagebox.showinfo(UNSUCCESSFUL_LOGIN, USER_NOT_FOUND, icon="warning", parent=root)


def reset():
    dirname = ""
    valid_dir = False
    images = []
    act_name = ""
    step = 0
    preview.pack_forget()
    select_folder['state'] = 'normal'
    instruct.update()

def end():
    global user, rank, m_name, images
    os.rmdir(TEMP_FOLDER_NAME)
    recordData(user, m_name.get(), str(len(images)), rank)
    if (shutdown_on_finish.get()):
        os.system("shutdown /s")
    else:
        reset()
    

first_step()
root.mainloop()
