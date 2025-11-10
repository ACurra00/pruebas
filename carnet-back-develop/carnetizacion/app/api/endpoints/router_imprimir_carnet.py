from http.client import HTTPResponse
from io import BytesIO
import json
import requests
import base64
from PIL import Image,ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from db.models.person import Person
import zipfile
from zipfile import ZipFile
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Response
from fastapi.responses import StreamingResponse
from db.repository.folio_cont import buscar_folio_por_nombre
from db.session import get_db
from db.models.carnet_activo import CarnetActivo
from schemas.carnet_activo import CarnetActivoCreate,ShowCarnetActivo
from db.repository.carnet_activo import lista_solicitados_consejo, lista_solicitados_externo, lista_solicitados_cuadros, retreive_carnet, lista_solicitados, update_state_carnet, lista_solicitados_docente, update_folio_carnet, lista_solicitados_ex, lista_solicitado_becado_asistido, lista_solicitado_extranjero_externo
from db.repository.person import retreive_person
from db.repository.folio_cont import retreive_last_folio_cont, update_folio_by_id,update_folio_by_name_and_only_number
from db.repository.carnet_activo import get_carnet_by_ci
from schemas.folio_cont import Folio_ContCreate
from db.repository.carnet_activo import lista_solicitados_no_docente, lista_solicitados_seminterno, lista_solicitados_becado, lista_solicitados_becado_ex
# from fpdf import FPDF

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab_qrcode import QRCodeImage
from reportlab.graphics.barcode import code39
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPM
from barcode.writer import ImageWriter
from barcode.writer import SVGWriter
from barcode.codex import Code39

import os
import qrcode
import barcode
from barcode.writer import ImageWriter
from textwrap import wrap
import textwrap
from typing import List
from starlette.responses import FileResponse
from datetime import datetime
import datetime

from db.repository.registro import create_new_registro

router = APIRouter()


def buscar_personas_por_ci(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/dss/search-matriculate"

    # Extrae las credenciales de autenticación del nuevo endpoint
    username = "disertic-web"
    password = "disertic-web841109"

    # Construye la autorización básica
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headersList = {
        "Accept": "*/*",
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }

    # Prepara el payload con el id de la carrera
    payload = {
        "identification": ci,
        "lastName": "",
        "firstName": "",
        "middleName": "",
        "idCareer": "",  # Utiliza el parámetro 'area' como idCareer
        "idCourseType": "",
        "idSex": "",
        "idEntrySource": "",
        "idStudentStatus": ""
    }

    response = requests.request("POST", reqUrl, data=json.dumps(payload), headers=headersList)
    #print(response.text)
    users = json.loads(response.text)

    return users


def buscarTrabajdor_and_Estudiante(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-ldap-cujae/ldap/search-all"

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": "Basic ZGlzZXJ0aWMubGRhcDpkaXNlcnRpYyoyMDIyKmxkYXA=",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "identification": ci,
        "name": "",
        "lastname": "",
        "surname": "",
        "email": "",
        "area": ""
    })

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)

    result = json.loads(str(response.text))
    if (bool(result)):
        return result
    else:
        return None

def buscarFoto(ci: str):
    reqUrl = "https://sigenu.cujae.edu.cu/sigenu-rest/student/" + ci + "/photo-base64"

    # Extrae las credenciales de autenticación del nuevo endpoint
    username = "disertic-web"
    password = "disertic-web841109"

    # Construye la autorización básica
    auth_string = f"{username}:{password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headersList = {
        "Accept": "*/*",
        "Authorization": f"Basic {encoded_auth}"
    }

    response = requests.request("GET", reqUrl, headers=headersList)

    return response.text

def crear_pdf(list: List, folio: str, nombre:str, db: Session):
  numero_1 =0
  numero_2= 0
  numero_3= 0
  numero_4= 0
  numero_5= 0
  fecha= str(datetime.date.today())
  temp = nombre + "-fecha: " + fecha + ".pdf"
  #print("estoy aqui 1"+ temp)
  doc = canvas.Canvas(temp)
  pdfmetrics.registerFont(TTFont('Calibri-Bold', 'calibrib.ttf'))
  i =0
  Folio_temp = buscar_folio_por_nombre(folio,db)
  numero_1= Folio_temp.numero_1
  numero_2= Folio_temp.numero_2
  numero_3= Folio_temp.numero_3
  numero_4= Folio_temp.numero_4
  numero_5= Folio_temp.numero_5
  cantidad_hojas= Folio_temp.cantidad_hojas
  hoja_actual =1
  for carnet in list:
     img = None
     #print("El carnet")
     #print(carnet.CarnetActivo.person_ci)
     ci = carnet.CarnetActivo.person_ci
     print("El ci es " + ci)
     person = buscar_personas_por_ci(ci)
     print("La persona es :")
     print(person)
     if person != []:
       user = person[0]
       img = user['photoBase64']
     else:
       print("Esta buscando la foto de la persona en el endpoint de promovidos")
       person = buscarTrabajdor_and_Estudiante(ci)
       user = person[0]
       img = user['photoBase64']
     if(hoja_actual<= cantidad_hojas):
      #print(carnet)
      c,p=carnet

      update_state_carnet(id=c.id,db=db)

      carnet_activo = c
      current_person = p
      doc.setFont("Calibri-Bold", 14)
      doc.setFillAlpha(1.0)
      if(i==0):
         #print("Entro al 0")

         update_folio_carnet(c.id, numero_1, db=db)
         numero_1 = numero_1 +1     #se actualizo el folio
         update_folio_by_name_and_only_number(folio,numero=numero_1,column=i,db=db)

         y_nombre= 10.27*inch
         y_nombre_w = 10.08*inch
         y_area = 9.96*inch
         y_area_w = 9.85*inch
         y_ci = 9.7*inch
         y_qr = 9.58*inch #======================================
         y_code = 9.36*inch

         y_acceso =9.48*inch
         y_rect = 9.46*inch
         y_imag = 9.94*inch
      elif(i==1):

         update_folio_carnet(c.id, numero_2, db=db)
         numero_2 = numero_2 +1     #se actualizo el folio
         update_folio_by_name_and_only_number(folio,numero=numero_2,column=i,db=db)

         y_nombre= 8.07*inch
         y_nombre_w = 7.88*inch
         y_area = 7.76*inch
         y_area_w = 7.65*inch
         y_ci = 7.5*inch
         y_qr = 7.38*inch #=========================================
         y_code = 7.16*inch

         y_acceso =7.28*inch
         y_rect = 7.26*inch
         y_imag = 7.74*inch
         #print("Entro al 1")

      elif(i==2):
         update_folio_carnet(c.id, numero_3, db=db)
         numero_3 = numero_3 +1     #se actualizo el folio
         update_folio_by_name_and_only_number(folio,numero=numero_3,column=i,db=db)

         y_nombre= 5.93*inch
         y_nombre_w = 5.74*inch
         y_area = 5.62*inch
         y_area_w = 5.51*inch
         y_ci = 5.36*inch
         y_qr = 5.24*inch
         y_code = 5.02 *inch

         y_acceso = 5.14 *inch
         y_rect = 5.12 *inch
         y_imag = 5.6 *inch
         #print("Entro al 2")

      elif(i==3):
         update_folio_carnet(c.id, numero_4, db=db)
         numero_4 = numero_4 +1     #se actualizo el folio
         update_folio_by_name_and_only_number(folio,numero=numero_4,column=i,db=db)

         y_nombre= 3.77*inch
         y_nombre_w = 3.58*inch
         y_area = 3.46*inch
         y_area_w = 3.35*inch
         y_ci = 3.2*inch
         y_qr = 3.08*inch
         y_code = 2.86*inch

         y_acceso =2.98*inch
         y_rect = 2.96*inch
         y_imag = 3.44*inch

      elif(i==4):
         update_folio_carnet(c.id, numero_5, db=db)
         numero_5 = numero_5 +1     #se actualizo el folio
         update_folio_by_name_and_only_number(folio,numero=numero_5,column=i,db=db)

         y_nombre= 1.6*inch
         y_nombre_w = 1.41*inch
         y_area = 1.29*inch
         y_area_w =1.18*inch
         y_ci = 1.03*inch
         y_qr = 0.91*inch
         y_code = 0.69*inch

         y_acceso =0.81*inch
         y_rect = 0.79*inch
         y_imag = 1.27*inch
         #print("Entro al 4")

      doc.setStrokeColorRGB(0.61, 0.61, 0.61)
      doc.rect(0.98*inch, y_rect, 65, 65)

      if img is not None:
        img_data = base64.b64decode(img)
        img_file = BytesIO(img_data)
        try:
         image = Image.open(img_file)
         max_size = (65, 65)  # Tamaño máximo del rectángulo
         image.thumbnail(max_size)
         rl_image = ImageReader(image)
         #doc.drawImage('firma2.png', 5.83*inch , y_imag, width=50, height=50)
         doc.drawImage(rl_image, 0.98 * inch, y_rect, width=image.size[0], height=image.size[1])
        except IOError:
            print("El archivo de imagen parece estar corrupto")

      if len(current_person.nombre) > 22:
         wrap_text = textwrap.wrap(current_person.nombre, width=22)
         doc.drawString(1.93*inch,y_nombre, wrap_text[0])
         if len(wrap_text) > 1:
             doc.drawString(1.93 * inch, y_nombre_w, wrap_text[1])
      else:
         doc.drawString(1.93*inch,y_nombre, current_person.nombre)
      doc.setFont("Calibri-Bold", 10)
      if len(current_person.area) > 23:
         wrap_text = textwrap.wrap(current_person.area, width=23)
         doc.drawString(1.93*inch,y_area, wrap_text[0])
         doc.drawString(1.93*inch,y_area_w, wrap_text[1])
      else:
         doc.drawString(1.93*inch,y_area_w, current_person.area)
      doc.setFont("Calibri-Bold", 10)

      doc.drawString(1.93*inch,y_ci, current_person.ci)
      doc.setFont("Calibri-Bold", 19)

      if folio == "docentes" or folio == "cuadros" or folio == "consejos":
         doc.drawString(1.93*inch,y_acceso,"Docente") # Aqui la funcioa de buscar si la persona es de libre acceso o no
      if folio == "no docentes":
          doc.drawString(1.93 * inch, y_acceso, "No docente")
      if folio == "seminterno":
         doc.drawString(1.93*inch,y_acceso,"Seminterno")
      if folio == "externos":
         doc.drawString(1.93*inch,y_acceso,"Externo")
      if folio == "becados":
         doc.drawString(1.93 * inch, y_acceso, "Becado Nacional")
      if folio == "becados extranjeros":
         doc.drawString(1.93 * inch, y_acceso, "Becado Extranjero")
      if folio == "becado nacional asistido":
          doc.drawString(1.93 * inch, y_acceso, "Becado Asistido")
      if folio == "extranjero externo":
          doc.drawString(1.93 * inch, y_acceso, "Extranjero Externo")
      qrtxt = ("N:" + current_person.nombre + ",CI:" + current_person.ci + ",A:" + current_person.area + ",F:" + str(carnet_activo.folio))
      qr = QRCodeImage(qrtxt, size=2.5*cm)
      qr.drawOn(doc, 4.26*inch,y_qr)
      code=str(current_person.ci)
      barcode=code39.Extended39(code,barWidth=0.4*mm,barHeight=5.62*mm)
      barcode.drawOn(doc, 4.1*inch, y_code)

      #Marca de agua original
      marca_agua_path = os.path.join(os.path.dirname(__file__), 'cujae.png')
      marca_agua = Image.open(marca_agua_path).convert("RGBA")
      marca_agua.thumbnail((50, 50))
      rl_marca_agua = ImageReader(marca_agua)
      doc.drawImage(rl_marca_agua, 5.21* inch, y_qr, width=marca_agua.size[0], height=marca_agua.size[1])

      # Marca de agua nuevo
      watermark_text = "cujae"
      doc.setFont("Calibri-Bold", 30)
      doc.setFillAlpha(0.2)
      for y in range(0, int(letter[1]), 100):
          for x in range(0, int(letter[0]), 100):
              doc.drawString(x, y, watermark_text)

      i+=1
      if(i == 5):
         doc.showPage()
         hoja_actual +=1
         i=0
     else:
        print("Hoja Actual mayor que cantidad de hojas permitidas")
        d = 2
  doc.save()
  env_path = Path(".") / ".env"
  load_dotenv(dotenv_path=env_path)

  return temp


def crear_imagen(list, folio: str, nombre: str, db):
    fecha = str(datetime.date.today())
    #temp = nombre + "-fecha: " + fecha + ".png"

    # Crear una imagen en blanco
    ancho, alto = 1024, 768  # Dimensiones ajustadas para el modelo
    imagen = Image.new("RGB", (ancho, alto), "white")
    dibujar = ImageDraw.Draw(imagen)

    # Cargar la fuente
    try:
        fuente = ImageFont.truetype("calibrib.ttf", 20)
        fuente_bold = ImageFont.truetype("calibrib.ttf", 30)
        fuente_marca_agua = ImageFont.truetype("calibrib.ttf", 40)
    except IOError:
        fuente = ImageFont.load_default()
        fuente_bold = ImageFont.load_default()
        fuente_marca_agua = ImageFont.load_default()

    Folio_temp = buscar_folio_por_nombre(folio, db)
    numero_1 = Folio_temp.numero_1
    cantidad_hojas = Folio_temp.cantidad_hojas
    hoja_actual = 1

    for carnet in list:
        img = None
        ci = carnet.CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)

        if person != []:
            user = person[0]
            img = user['photoBase64']
        else:
            print("Esta buscando la foto de la persona en el endpoint de promovidos")
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
            img = user['photoBase64']

        if hoja_actual <= cantidad_hojas:
            c, p = carnet
            update_state_carnet(id=c.id, db=db)

            carnet_activo = c
            current_person = p

            # Actualizar el folio
            update_folio_carnet(c.id, numero_1, db=db)
            numero_1 += 1
            update_folio_by_name_and_only_number(folio, numero=numero_1, column=0, db=db)

            # Dibuja un rectángulo para la foto
            pictureOriginY= 60
            dibujar.rectangle([25, pictureOriginY, 225, pictureOriginY + 200], outline="gray", width=2)
            temp = current_person.ci + "-fecha: " + fecha + ".png"
            if img is not None:
                img_data = base64.b64decode(img)
                img_file = BytesIO(img_data)
                try:
                    image = Image.open(img_file)
                    image.thumbnail((225, pictureOriginY + 200))  # Tamaño máximo
                    imagen.paste(image, (25, pictureOriginY))
                except IOError:
                    print("El archivo de imagen parece estar corrupto")

            # Escribir el nombre
            textOrigin = 240
            dibujar.text((textOrigin, 60), current_person.nombre, font=fuente_bold, fill="black")

            # Escribir el área
            dibujar.text((textOrigin, 120), current_person.area, font=fuente, fill="black")

            # Escribir el CI
            dibujar.text((textOrigin, 180), current_person.ci, font=fuente, fill="black")

            # Escribir tipo de acceso
            acceso_texto = {
                "docentes": "Docente",
                "no docentes": "No docente",
                "cuadros": "Docente",
                "consejos": "Docente",
                "seminterno": "Seminterno",
                "externos": "Externo",
                "becados": "Becado Nacional",
                "becados extranjeros": "Becado Extranjero",
                "becado nacional asistido": "Becado Nacional Asistido",
                "extranjero externo": "Extranjero Externo"
            }
            texto_acceso = acceso_texto.get(folio, "")
            dibujar.text((textOrigin, 240), texto_acceso, font=fuente_bold, fill="black")

            # Generar y colocar el código QR
            qrtxt = ("N:" + current_person.nombre + ",CI:" + current_person.ci + ",A:" + current_person.area + ",F:" + str(
                    carnet_activo.folio))
            qr = qrcode.QRCode(box_size=4, border=2)
            qr.add_data(qrtxt)
            qr.make(fit=True)
            qr_img_x = 685
            qr_img_y = 60
            qr_img = qr.make_image(fill="black", back_color="white").convert("RGB")
            qr_img = qr_img.resize((120, 120), Image.Resampling.LANCZOS)
            imagen.paste(qr_img, (qr_img_x, qr_img_y))

            # Dibujar el código de barras (placeholder gráfico)
            barcode_data = str(current_person.ci)
            #CODE = barcode.get_barcode_class('code39')
            code = Code39(barcode_data , writer=ImageWriter())
            #barcode_image = code.save('code39Image')
            buffer = BytesIO()
            code.write(buffer, options={'write_text': False})
            barcode_image = Image.open(buffer).resize((300, 50), Image.Resampling.LANCZOS)
            qr_y_end = qr_img_y + qr_img.height
            barcode_x = qr_img_x - 10
            barcode_y = qr_y_end + 50
            imagen.paste(barcode_image, (barcode_x, barcode_y, barcode_image.width + barcode_x, barcode_image.height + barcode_y))

            # Cargar la imagen de la marca de agua original
            watermark_path = os.path.join(os.path.dirname(__file__), 'cujae.png')
            marca_agua = Image.open(watermark_path).convert("RGBA")
            marca_agua.thumbnail((300, 50))  # Ajustar el tamaño de la marca de agua
            # Calcular la posición de la marca de agua
            marca_agua_x = qr_img_x + qr_img.width + 26  # Un poco a la derecha del código QR
            marca_agua_y = qr_img_y  # Misma altura que el código QR # Un poco debajo del código de barras
            imagen.paste(marca_agua, (marca_agua_x, marca_agua_y), marca_agua)

            # Aquí agregamos la marca de agua nueva
            watermark_text = "cujae"
            watermark_opacity = 50  # Opacidad de la marca de agua (0-255)
            watermark_color = (169, 169, 169, watermark_opacity)  # Color de la marca de agua
            ancho_marca_agua, alto_marca_agua = dibujar.textbbox((0, 0), watermark_text, font=fuente_marca_agua)[2:4]
            for i in range(0, ancho, ancho_marca_agua + 100):
                for j in range(0, alto, alto_marca_agua + 100):
                    dibujar.text((i, j), watermark_text, font=fuente_marca_agua, fill=watermark_color)

        else:
            print("Hoja actual mayor que la cantidad permitida")

    # Guardar la imagen
    imagen.save(temp, "PNG")
    return temp

@router.get("/imprimir_carnets_solicitados")
def print_carnets_solicitado(db: Session = Depends(get_db), current_user: str = None, carnet_id: str = None):
    print("Esta entrando al solo")
    if carnet_id is not None:
        print("CArnetID:")
        print(carnet_id)
        carnet = get_carnet_by_ci(db, carnet_id)
        print("Fetch de carnet y persona:")
        print(carnet)
        print("Carnet en cero")
        print(carnet[0])
        if (carnet[0].Person.rol == "Seminterno"):
            pdf = crear_imagen(list=carnet, folio="seminterno", nombre="Estudiante Seminterno", db=db)
        if (carnet[0].Person.rol == "Becado Nacional"):
            pdf = crear_imagen(list=carnet, folio="becados", nombre="Estudiante Becado", db=db)
        if (carnet[0].Person.rol == "Externo"):
            pdf = crear_imagen(list=carnet, folio="externos", nombre="Externo", db=db)
        if (carnet[0].Person.rol == "Docente"):
            pdf = crear_imagen(list=carnet, folio="docentes", nombre="Trabajador Docente", db=db)
        if (carnet[0].Person.rol == "No Docente"):
            pdf = crear_imagen(list=carnet, folio="no docentes", nombre="Trabajador_No_Docente", db=db)
        # Retornar el PDF generado
        #files = [pdf]
        io = BytesIO()
        areaZip = "final_archive"
        if len(carnet) > 0:
            ci = carnet[0].CarnetActivo.person_ci
            person = buscar_personas_por_ci(ci)
            if len(person) > 0:
              user = person[0]
            else:
                person = buscarTrabajdor_and_Estudiante(ci)
                user = person[0]
            areaZip = user['area']

        fecha = str(datetime.date.today())
        if areaZip == "final_archive":
            zip_sub_dir = "final_archive"
        else:
            zip_sub_dir = f"{areaZip} {fecha}"
        zip_filename = "%s.zip" % zip_sub_dir
        with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
            # with ZipFile('my_python_files.zip','w') as zip:
            #for file in files:
                zip.write(pdf)
        zip.close()
        username = current_user.nombre_usuario
        accion = "El usuario imprimió un carnet como foto " + str(carnet_id)
        tipo = "Imprimir carnet"
        log = create_new_registro(db, username, accion, tipo)
        return StreamingResponse(
            iter([io.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment;filename=%s" % zip_filename}
        )

@router.post("/imprimir_carnets_solicitados_por_tipos_fotos")
# def print_carnet_activo(array: List[int] = Query(...),db: Session = Depends(get_db)):
def print_carnets_solicitados_por_tipo_fotos(current_user: str = None, db: Session = Depends(get_db)):
    print("Entrando al método para generar carnets lotes fotos")

    # Obtener las listas de cada tipo
    carnets = lista_solicitados(db=db)
    docente = lista_solicitados_docente(db=db)
    no_docente = lista_solicitados_no_docente(db=db)
    seminterno = lista_solicitados_seminterno(db=db)
    becado = lista_solicitados_becado(db=db)
    becado_ex = lista_solicitados_becado_ex(db=db)
    ex = lista_solicitados_ex(db=db)
    cuadros = lista_solicitados_cuadros(db=db)
    consejo = lista_solicitados_consejo(db=db)
    externo = lista_solicitados_externo(db=db)

    # Diccionario para facilitar el manejo de datos
    categorias = {
        "docentes": (docente, "Trabajador Docente"),
        "no_docentes": (no_docente, "Trabajador_No_Docente"),
        "seminterno": (seminterno, "Estudiante Seminterno"),
        "becados": (becado, "Estudiante_Becado"),
        "becados_ex": (becado_ex, "Estudiante_Becado_Extranjero"),
        "extranjeros": (ex, "Estudiante_Extranjero"),
        "consejos": (consejo, "Consejo Universitario"),
        "cuadros": (cuadros, "Cuadros"),
        "externos": (externo, "Externo"),
    }

    # Crear lista para almacenar rutas de imágenes generadas
    archivos_generados = []

    # Recorrer cada categoría y generar imágenes
    for folio, (lista, nombre) in categorias.items():
        for item in lista:
            # Llamar al método crear_imagen para cada elemento individualmente
            archivo = crear_imagen(list=[item], folio=folio, nombre=nombre, db=db)
            archivos_generados.append(archivo)

    # Crear un archivo ZIP y añadir los carnets generados
    io = BytesIO()
    areaZip = "final_archive"
    if len(seminterno) > 0:
        ci = seminterno[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        user = person[0]
        areaZip = user['area']
    if len(docente) > 0:
        ci = docente[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        if len(person) > 0:
            user = person[0]
        else:
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
        areaZip = user['area']
    if len(no_docente) > 0:
        ci = no_docente[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        if len(person) > 0:
            user = person[0]
        else:
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
        areaZip = user['area']
    if len(externo) > 0:
        ci = externo[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        if len(person) > 0:
            user = person[0]
        else:
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
        areaZip = user['area']
    if len(becado) > 0:
        ci = becado[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        if len(person) > 0:
            user = person[0]
        else:
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
        areaZip = user['area']
    if len(becado_ex) > 0:
        ci = becado_ex[0].CarnetActivo.person_ci
        person = buscar_personas_por_ci(ci)
        if len(person) > 0:
            user = person[0]
        else:
            person = buscarTrabajdor_and_Estudiante(ci)
            user = person[0]
        areaZip = user['area']

    fecha = str(datetime.date.today())
    if areaZip == "final_archive":
        zip_sub_dir = "final_archive"
    else:
        zip_sub_dir = f"{areaZip} {fecha}"
    zip_filename = f"{zip_sub_dir}.zip"

    with zipfile.ZipFile(io, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for archivo in archivos_generados:
            zip_file.write(archivo)
    io.seek(0)
    username = current_user.nombre_usuario
    accion = "El usuario imprimió carnets en lote como foto"
    tipo = "Imprimir carnet"
    log = create_new_registro(db, username, accion, tipo)
    # Retornar el archivo ZIP como respuesta
    return StreamingResponse(
        iter([io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename={zip_filename}"}
    )

@router.post("/imprimir_carnets_solicitados_por_tipos")
# def print_carnet_activo(array: List[int] = Query(...),db: Session = Depends(get_db)):
def print_carnets_solicitados_por_tipo(current_user: str = None, db: Session = Depends(get_db)):
   print("Esta entrando al multiple")
   # zip = ZipFile(response, 'w')
   # mem_zip = BytesIO()
   # files=[]
   carnets=lista_solicitados(db=db)
   docente=lista_solicitados_docente(db=db)
   no_docente = lista_solicitados_no_docente(db=db)
   seminterno = lista_solicitados_seminterno(db=db)
   becado= lista_solicitados_becado(db=db)
   becado_ex = lista_solicitados_becado_ex(db=db)
   #becado_asist = lista_solicitado_becado_asistido(db=db)
   ex=lista_solicitados_ex(db=db)
   cuadros=lista_solicitados_cuadros(db=db)
   consejo=lista_solicitados_consejo(db=db)
   externo = lista_solicitados_externo(db=db)
   #extern_extra = lista_solicitado_extranjero_externo(db=db)



   doc_docente = crear_pdf(list=docente, folio="docentes", nombre="Trabajador Docente", db=db)
   doc_n_docent = crear_pdf(list=no_docente, folio="no docentes", nombre="Trabajador_No_Docente", db=db)
   doc_seminterno = crear_pdf(list=seminterno, folio="seminterno", nombre="Estudiante Seminterno", db=db)
   doc_becado = crear_pdf(list=becado, folio="becados", nombre="Estudiante_Becado", db=db)
   doc_becado_ex = crear_pdf(list=becado_ex, folio="becados extranjeros", nombre="Estudiante_Becado_Extranjero", db=db)
   doc_ex = crear_pdf(list=ex, folio="extranjeros", nombre="Estudiante_Extranjero", db=db)
   doc_consejo=crear_pdf(list=consejo, folio="consejos", nombre="Consejo Universitario", db=db)
   doc_cuadros=crear_pdf(list=cuadros, folio="cuadros", nombre="Cuadros", db=db)
   doc_externo=crear_pdf(list=externo, folio="externos", nombre="Externo", db=db)
   #doc_beacasit = crear_pdf(list=becado_asist, folio="becado nacional asistido", nombre="Becado Asistido", db=db)
   #doc_extranje_ext = crear_pdf(list=extern_extra, folio="extranjero externo", nombre="Extranjero Externo", db=db)
   files=[doc_docente,doc_n_docent,doc_seminterno, doc_becado, doc_becado_ex, doc_ex, doc_externo, doc_consejo, doc_cuadros]
   io = BytesIO()

   print("Docente")
   print(docente)
   areaZip = "final_archive"
   if len(seminterno) > 0:
     ci = seminterno[0].CarnetActivo.person_ci
     person = buscar_personas_por_ci(ci)
     if len(person) > 0:
         user = person[0]
     else:
         person = buscarTrabajdor_and_Estudiante(ci)
         user = person[0]
     areaZip = user['area']
   if len(docente) > 0:
       ci = docente[0].CarnetActivo.person_ci
       person = buscar_personas_por_ci(ci)
       if len(person) > 0:
           user = person[0]
       else:
           person = buscarTrabajdor_and_Estudiante(ci)
           user = person[0]
       areaZip = user['area']
   if len(no_docente) > 0:
       ci = no_docente[0].CarnetActivo.person_ci
       person = buscar_personas_por_ci(ci)
       if len(person) > 0:
           user = person[0]
       else:
           person = buscarTrabajdor_and_Estudiante(ci)
           user = person[0]
       areaZip = user['area']
   if len(externo) > 0:
       ci = externo[0].CarnetActivo.person_ci
       person = buscar_personas_por_ci(ci)
       if len(person) > 0:
           user = person[0]
       else:
           person = buscarTrabajdor_and_Estudiante(ci)
           user = person[0]
       areaZip = user['area']
   if len(becado) > 0:
       ci = becado[0].CarnetActivo.person_ci
       person = buscar_personas_por_ci(ci)
       if len(person) > 0:
           user = person[0]
       else:
           person = buscarTrabajdor_and_Estudiante(ci)
           user = person[0]
       areaZip = user['area']
   if len(becado_ex) > 0:
       ci = becado_ex[0].CarnetActivo.person_ci
       person = buscar_personas_por_ci(ci)
       if len(person) > 0:
           user = person[0]
       else:
           person = buscarTrabajdor_and_Estudiante(ci)
           user = person[0]
       areaZip = user['area']

   fecha = str(datetime.date.today())
   if areaZip == "final_archive":
       zip_sub_dir = "final_archive"
   else:
       zip_sub_dir = f"{areaZip} {fecha}"
   zip_filename = "%s.zip" % zip_sub_dir
   with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
   # with ZipFile('my_python_files.zip','w') as zip:
        for file in files:
            zip.write(file)
   zip.close()
   username = current_user.nombre_usuario
   accion = "El usuario imprimió carnets en lote como pdf"
   tipo = "Imprimir carnet"
   log = create_new_registro(db, username, accion, tipo)
   return StreamingResponse(
        iter([io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers = { "Content-Disposition":f"attachment;filename=%s" % zip_filename}
    )

