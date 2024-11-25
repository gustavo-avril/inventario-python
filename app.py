from flask import Flask, request, render_template, send_file
import PyPDF2
import pdfkit
from io import BytesIO
import re
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():

    if 'pdf_file' not in request.files:
        return 'No file part'
    
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No selected file'
    
    selected_template = request.form['template']
    selected_language = request.form['language']

    # Concatenar los valores para crear el nombre del archivo de plantilla
    template_name = f"{selected_template}{selected_language}.html"

    # Verificar si la plantilla existe
    if not os.path.exists(os.path.join('templates', template_name)):
        return f"Error: La plantilla {template_name} no existe."
        
    # Extraer texto del PDF
    pdf_reader = PyPDF2.PdfReader(file)
    extracted_text = ""
    for page in pdf_reader.pages:
      extracted_text += page.extract_text() + "\n"
    
    # Definir las variables usando expresiones regulares
    voucher = re.search(r'VOUCHER Nº:\s*(\S+)', extracted_text).group(1)
    nombre = re.search(r'APELLIDO y NOMBRE:\s*(.*)', extracted_text).group(1)
    # Verificar si existe el campo "PASAPORTE" o "DNI"
    pasaporte_match = re.search(r'PASAPORTE\s*(\S+)', extracted_text)
    dni_match = re.search(r'DNI\s*(\S+)', extracted_text)
    
    if pasaporte_match:
      pasaporte = pasaporte_match.group(1)
    elif dni_match:
      pasaporte = dni_match.group(1)
    else:
      pasaporte = "No disponible"

    fecha_nacimiento = re.search(r'FECHA DE NACIMIENTO:\s*(\S+)', extracted_text).group(1)
    plan = re.search(r'PLAN:\s*(.*)', extracted_text).group(1)
    destino = re.search(r'DESTINO:\s*(.*)', extracted_text).group(1)
    # Modificar la expresión regular para capturar la vigencia correctamente
    vigencia_match = re.search(r'VIGENCIA:\s*DEL\s*(\S+)\s*AL\s*(\S+)', extracted_text)
    
    if vigencia_match:
      vigencia_del = vigencia_match.group(1)
      vigencia_al = vigencia_match.group(2)
    else:
      vigencia_del = "No disponible"
      vigencia_al = "No disponible"

    fecha_emision = re.search(r'FECHA DE EMISION:\s*(\S+)', extracted_text).group(1)
    contacto_emergencia_match = re.search(r'CONTACTO EMERGENCIA:\s*(.*)', extracted_text)
    if contacto_emergencia_match:
      contacto_emergencia = contacto_emergencia_match.group(1)
    else:
      contacto_emergencia = ""
    
    telefono_match = re.search(r'TEL\.\s*(.*)', extracted_text)
    if telefono_match:
      telefono = telefono_match.group(1)
    else:
      telefono = ""
    agencia = re.search(r'AGENCIA:\s*(.*)', extracted_text).group(1)

    # Renderizar la plantilla HTML
    html = render_template(template_name, 
                            voucher=voucher,
                            nombre=nombre,
                            pasaporte=pasaporte,
                            fecha_nacimiento=fecha_nacimiento,
                            plan=plan,
                            destino=destino,
                            vigencia_del=vigencia_del,
                            vigencia_al=vigencia_al,
                            fecha_emision=fecha_emision,
                            contacto_emergencia=contacto_emergencia,
                            telefono=telefono,
                            agencia=agencia)

    # Convertir HTML a PDF usando pdfkit
    # pdf_output = pdfkit.from_string(html, False, configuration=config)
    pdf_output = pdfkit.from_string(html, False)

    return send_file(BytesIO(pdf_output), as_attachment=True, download_name=nombre + "-" + selected_language.upper() +  ".pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
    