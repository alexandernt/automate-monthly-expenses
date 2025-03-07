import pdfplumber
import re
import pandas as pd

csv_month = "202503" # <<<<----- PLEASE, MODIFY IT ACCORDINGLY
report_month = '2025-03-01' # <<<<----- PLEASE, MODIFY IT ACCORDINGLY 
csv_name = "__naranjax"
input_pdf_file_path = f"input/pdf/{csv_month}{csv_name}.pdf"
output_pdf_file_path = f"output/csv/{csv_month}{csv_name}.csv"

def extract_consumos(pdf_path):

    consumos = []

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Patrón para encontrar consumos en pesos argentinos (ARS)
    pattern_pesos = re.findall(
        r"(\d{2}/\d{2}/\d{2})\s+NX Visa\s+\d+\s+([\w\s\.\*\(\),%-]+?)\s+\d+\s+([\d\.]+,\d{2})",
        text
    )

    # Patrón para encontrar consumos en dólares (USD)
    pattern_dolares = re.findall(
        r"(\d{2}/\d{2}/\d{2})\s+NX Visa\s+\d+\s+([\w\s\.\*\:\-]+)\s+(\d+,\d{2})", 
        text
    )

    # Patrón para otros cargos (como comisiones)
    pattern_cargos = re.findall(
        r"(\d{2}/\d{2}/\d{2})\s+\*([\w\s\.\*]+)\s+([\d\.]+,\d{2})", 
        text
    )


    # Función para asignar subcategoría en base a detalles
    def assign_subcategory(details):
        if "EXPRESS" in details.upper() or "RES" in details.upper() or "DAR" in details.upper() or "COTO" in details.upper():
            return "grocery"
        elif "FARMACITY" in details.upper():
            return "pharmacy"
        elif "OSDE" in details.upper():
            return "health_care"
        elif "MANTENIMIENTO" in details.upper():
            return "bank_account_fees"
        elif "OPENAI" in details.upper() or "GRID" in details.upper() or "STEAM" in details.upper()  or "OPENAI" in details.upper():
            return "personal"
        elif "MERPAGO MERCADOLIBRE" in details.upper():
            return "online_shopping"
        elif "METROGAS" in details.upper() or "YPF" in details.upper() or "EDENOR" in details.upper() or "PERSONALFLOW" in details.upper():
            return "services"
        elif "UBER" in details.upper() or "CABIFY" in details.upper() or "DIDI" in details.upper() or "TAXI" in details.upper() or "PASAJESCDP" in details.upper():
            return "transportation"
        else:
            return "other"

    # Procesar consumos en pesos (ARS)
    for match in pattern_pesos:
        fecha, detalle, monto = match
        monto = float(monto.replace('.', '').replace(',', '.').replace('-',''))  
        fecha = "20" + "-".join(reversed(fecha.split("/")))  
        consumos.append({
            "report_month": report_month,
            "event_date": fecha, 
            "details": detalle.strip(), 
            "amount": monto, 
            "currency": "ARS", 
            "category": "credit_card_naranjax", 
            "subcategory": assign_subcategory(detalle)
        })

    # Procesar consumos en dólares (USD)
    for match in pattern_dolares:
        fecha, detalle, monto = match
        monto = float(monto.replace(',', '.').replace('-','')) 
        fecha = "20" + "-".join(reversed(fecha.split("/")))  
        consumos.append({
            "report_month": report_month,
            "event_date": fecha, 
            "details": detalle.strip(), 
            "amount": monto, 
            "currency": "USD", 
            "category": "credit_card_naranjax", 
            "subcategory": assign_subcategory(detalle)      
        })

    # Procesar otros cargos (comisiones, impuestos, etc.)
    for match in pattern_cargos:
        fecha, detalle, monto = match
        monto = float(monto.replace('.', '').replace(',', '.').replace('-',''))  
        fecha = "20" + "-".join(reversed(fecha.split("/")))  
        consumos.append({
            "report_month": report_month,
            "event_date": fecha, 
            "details": detalle.strip(), 
            "amount": monto, 
            "currency": "ARS", 
            "category": "credit_card_naranjax", 
            "subcategory": assign_subcategory(detalle)
        })

    df = pd.DataFrame(consumos)
    return df

# Extraer los consumos
df_consumos = extract_consumos(input_pdf_file_path)

# Guardar en CSV
df_consumos.to_csv(output_pdf_file_path, index=False)
print(f"Archivo {output_pdf_file_path} guardado con éxito.")

# Mostrar en consola
print(df_consumos)