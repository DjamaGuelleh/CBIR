

# -*- coding: utf-8 -*-
"""
Created on Thu May 12 23:28:38 2022

@author: Djama
"""
########################################################___Modules_importer____####################################
import matplotlib.pyplot as plt 
from tqdm import tqdm
import json
import os 
from mahotas.features import zernike_moments
import cv2 as cv
import numpy as np
import math
from math import dist
from typing import List
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog
from pathlib import Path
from tkinter import *
from PIL import ImageTk, Image
import sys



#################################################___Fonctions_de_Traitements____################################

def SortDict(dict1):
    """fonction pour trier un dictionnaire"""
    sorted_values = sorted(dict1.values()) 
    sorted_dict = {}

    for i in sorted_values:
        for k in dict1.keys():
            if dict1[k] == i:
                sorted_dict[k] = dict1[k]
                break
    return sorted_dict

def histoRGB(img_path,bins) :
    """fonction pour calculer l'histogramme en RGB
    d'une image en fonction des bins """
    img=cv.imread(img_path)
    histobin ,bins_  = np.histogram(img.ravel(),int(bins), [0,256])
    histobin = histobin / (max(histobin) - min(histobin) )
    return histobin 

def histoHSV(img_path,bins):
    """fonction pour calculer l'histogramme en HSV
    d'une image en fonction des bins  """
    img=cv.imread(img_path)
    hsvImg = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    histobin ,bins_  = np.histogram(hsvImg.ravel(), int(bins), [0,256])
    histobin = histobin / (max(histobin) - min(histobin) )
    return histobin


def swain(hist1,hist2):
    """cette fonction implemente la distance de Swain"""
    d = 0
    for i in range(0,len(hist2)):
        d += min(hist1[i],hist2[i])/(sum(hist2))
    return (1-d)

def disthistobin(histreq,hist):
    """cette fonction implemente la distance euclidienne entre 
    deux histogrammes de deux images distinct """
    d = abs(hist-histreq)
    dist = sum(d) /sum(hist)    
    return dist
    
def to_gray(img):
    """cette fonction permet de transformer une 
    image RGB en nuance de gris """
    w, h,_ = img.shape
    ret = np.empty((w, h), dtype=np.uint8)
    retf = np.empty((w, h), dtype=np.float)
    imgf = img.astype(float)
    retf[:, :] = ((imgf[:, :, 1] + imgf[:, :, 2] + imgf[:, :, 0])/3)
    ret = retf.astype(np.uint8)
    return ret




def zernick(img_path):
    """ il s'agit d'une fonction pour les calculs des moments
    de Zernick """
    img = cv.imread(img_path)

    img = to_gray(img)
    radius = 19
    value = zernike_moments(img,  radius)
    return value



def RGB(img_path,bins) :
    """ cette fonction calcul et retourne un dictionnaire contenant 
    comme cle les noms des images dans la base et comme valeur la distance entre 
    l'image requete et l'image en question, ces calcul de distance sont faites dans l'espace 
    RGB"""
    histreq = histoRGB(img_path,bins)
    index_bins = "index_RGB_coil_"+bins+".json"

    with open(index_bins, "r") as f:

        index_dict = {k: np.array(v) for k, v in tqdm(json.load(f).items())}

        f.close()

    result_dict = {}

    for cle , valeur in tqdm(index_dict.items()) :

                d = swain(hist2=valeur,hist1=histreq)

                result_dict[path +"/"+ cle] = d

    result_dict[img_path] =0   

    return result_dict

def HSV(img_path,bins):
    """ cette fonction calcul et retourne un dictionnaire contenant 
    comme cle les noms des images dans la base et comme valeur la distance entre 
    l'image requete et l'image en question, ces calcul de distance sont faites dans l'espace 
    HSV"""
    histreq = histoHSV(img_path,bins)

    index_bins = "index_HSV_coil_"+str(bins)+".json"

    with open(index_bins, "r") as f:
        index_dict = {k: np.array(v) for k, v in tqdm(json.load(f).items())}
        f.close()
    result_dict = {}
    for cle , valeur in tqdm(index_dict.items()) :
                d = swain(hist2=valeur,hist1=histreq)
                result_dict[path +"/"+ cle] = d
    result_dict[img_path] =0          
    
    return result_dict

def RGB_forme(pathreq,bins):
    """ Avec cette fonction on combine les methodes precedent notamment la comparaison 
    des histogrammes en RGB  avec un descripteur de forme 
    à savoir le moment de zernick """
    histreq = histoRGB(pathreq,bins)
    zer_req = zernick(pathreq)
    dict = {}
    dict[pathreq]= 0
    index_bins = "index_RGB_coil_"+str(bins)+".json"

    with open(index_bins, "r") as f:
        index_dict = {k: np.array(v) for k, v in tqdm(json.load(f).items())}
        f.close()
    with open("Index_Moments_coil_100.json", "r") as zernic:
        zer_dict = {k: np.array(v) for k, v in tqdm(json.load(zernic).items())}
        zernic.close()
    i = 0
    for cle , valeur in tqdm(index_dict.items()) :
            img = cv.imread(path +"/"+ cle)
            distancenorm =  disthistobin(histreq,valeur)
            #zer = zernick(img)
            zer = list(zer_dict.values())[i]
            i= i+1
            z = math.dist(zer,zer_req)
            dist_global = (0.6*distancenorm) + (0.4*z)
            dict[path +"/"+ cle]= dist_global
    dict[pathreq] =0 
       
    return dict    
        

def HSV_forme(pathreq,bins):
    """ Avec cette fonction on combine les methodes precedentes notamment la comparaison 
    des histogramme en HSV  avec un descripteur de forme 
    à savoir le moment de zernick """
    histreq = histoHSV(pathreq,bins)
    zer_req = zernick(pathreq)
    dict = {}
    dict[pathreq]= 0

    index_bins = "index_HSV_coil_"+str(bins)+".json"

    with open(index_bins, "r") as f:
        index_dict = {k: np.array(v) for k, v in tqdm(json.load(f).items())}
        f.close()
    with open("Index_Moments_coil_100.json", "r") as zernic:
        zer_dict = {k: np.array(v) for k, v in tqdm(json.load(zernic).items())}
        zernic.close()
    i = 0
    for cle , valeur in tqdm(index_dict.items()) :
            img = cv.imread(path +"/"+ cle)
            distancenorm =  disthistobin(histreq,valeur)
            #zer = zernick(img)
            zer = list(zer_dict.values())[i]
            i= i+1
            z = math.dist(zer,zer_req)
            dist_global = (0.6*distancenorm) + (0.4*z)
            dict[path +"/"+ cle]= dist_global
    dict[pathreq] =0    
    return dict    


######################################################CODE___GUI###################################################
# Path to asset files for this GUI window.
ASSETS_PATH = Path(__file__).resolve().parent / "assets"

# Required in order to add data files to Windows executable
path1 = getattr(sys, '_MEIPASS', os.getcwd())
os.chdir(path1)



path = "./coil-100"

def select_path():
    global path

    img_path = filedialog.askopenfilename(initialdir = path, title="choisir une image",filetype=(("png","*.png"),("jpeg","*.jpg")))
    path_entry.delete(0, tk.END)
    path_entry.insert(0, img_path)
    


def Plot_resultat():    
    bins = bins_entry.get()
    Descripteur = Descripteur_entry.get()
    img_path = path_entry.get()
    img_path = img_path.strip()
    
    dict={}
    
    if Descripteur == "RGB":
        dict = RGB(img_path,bins)
    if Descripteur == "HSV":
        dict = HSV(img_path,int(bins))
        
    if Descripteur == "forme":
        dict= forme(img_path,int(bins))
        
    if Descripteur == "HSV+forme":
        dict= HSV_forme(img_path,int(bins))
        
    if Descripteur == "RGB+forme":
        dict = RGB_forme(img_path,int(bins))
    
    
    dict_trier = SortDict(dict)
    image_chemin = list(dict_trier.keys())
    distances = list(dict_trier.values())
    plt.figure(figsize=(12,15))
    for i in range(12) : 
        plt.subplot(3,4,i+1)
        img = plt.imread(image_chemin[i])
        plt.imshow(img)
        if distances[i] ==0:
            plt.title("Image Requête")
        else :
            plt.title(distances[i])
        plt.axis('off')
    plt.show()

    

#code de l'interface Graphique 
window = tk.Tk()
logo = tk.PhotoImage(file=ASSETS_PATH / "ump_logo.png")
window.call('wm', 'iconphoto', window._w, logo)
window.title("CBIR interface")

window.geometry("862x519")
window.configure(bg="#3A7FF6")
canvas = tk.Canvas(
    window, bg="#3A7FF6", height=519, width=862,
    bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)
canvas.create_rectangle(431, 0, 431 + 431, 0 + 519, fill="#FCFCFC", outline="")
canvas.create_rectangle(40, 160, 40 + 60, 160 + 5, fill="#FCFCFC", outline="")

text_box_bg = tk.PhotoImage(file=ASSETS_PATH / "TextBox_Bg.png")
Descripteur_entry_img = canvas.create_image(650.5, 167.5, image=text_box_bg)
bins_entry_img = canvas.create_image(650.5, 248.5, image=text_box_bg)
filePath_entry_img = canvas.create_image(650.5, 329.5, image=text_box_bg)

Descripteur_entry = tk.Entry(bd=0, bg="#F6F7F9", highlightthickness=0)
Descripteur_entry.place(x=490.0, y=137+25, width=321.0, height=35)
Descripteur_entry.focus()

bins_entry = tk.Entry(bd=0, bg="#F6F7F9", highlightthickness=0)
bins_entry.place(x=490.0, y=218+25, width=321.0, height=35)

path_entry = tk.Entry(bd=0, bg="#F6F7F9", highlightthickness=0)
path_entry.place(x=490.0, y=299+25, width=321.0, height=35)

path_picker_img = tk.PhotoImage(file = ASSETS_PATH / "path_picker.png")
path_picker_button = tk.Button(
    image = path_picker_img,
    text = '',
    compound = 'center',
    fg = 'white',
    borderwidth = 0,
    highlightthickness = 0,
    command = select_path,
    relief = 'flat')

path_picker_button.place(
    x = 783, y = 319,
    width = 24,
    height = 22)

canvas.create_text(
    490.0, 156.0, text="Choix du Descripteur", fill="#515486",
    font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    490.0, 234.5, text="Choix de l'Histobins", fill="#515486",
    font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    490.0, 315.5, text="Image requête",
    fill="#515486", font=("Arial-BoldMT", int(13.0)), anchor="w")
canvas.create_text(
    646.5, 428.5, text="Chercher",
    fill="#FFFFFF", font=("Arial-BoldMT", int(13.0)))
canvas.create_text(
    573.5, 88.0, text="Entrer les Détails.",
    fill="#515486", font=("Arial-BoldMT", int(22.0)))

title = tk.Label(
    text="Welcome to CBIR", bg="#3A7FF6",
    fg="white", font=("Arial-BoldMT", int(20.0)))
title.place(x=27.0, y=120.0)

info_text = tk.Label(
    text="Choix des descripteur possible:\n"
    "RGB,HSV,RGB+forme,HSV+forme.\n\n"
    "Choix des Histobins possible:\n"
    "16,32,64,128,256\n\n"

    "Merci d'avoir choisi CBIR :) \n",
    bg="#3A7FF6", fg="white", justify="left",
    font=("Georgia", int(16.0)))

info_text.place(x=27.0, y=200.0)


generate_btn_img = tk.PhotoImage(file=ASSETS_PATH / "Capture.png")
generate_btn = tk.Button(
    image=generate_btn_img, borderwidth=0, highlightthickness=0,
    command=Plot_resultat, relief="flat")
generate_btn.place(x=557, y=401, width=180, height=55)


window.resizable(False, False)
window.mainloop()