import pdfplumber
import re
import pandas as pd

def extract_consumos(pdf_path):

    consumos = []
    report_month = '2025-02-01'

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
        elif "PERSONAL FLOW" in details.upper():
            return "internet"
        elif "OPENAI" in details.upper() or "GRID" in details.upper():
            return "personal"
        elif "MERPAGO MERCADOLIBRE" in details.upper():
            return "online_shopping"
        elif "METROGAS" in details.upper() or "YPF" in details.upper() or "EDENOR" in details.upper():
            return "services"
        elif "UBER" in details.upper() or "CABIFY" in details.upper() or "DIDI" in details.upper() or "TAXI" in details.upper() or "PASAJESCDP" in details.upper():
            return "transportation"
        else:
            return "other"

    # Procesar consumos en pesos (ARS)
    for match in pattern_pesos:
        fecha, detalle, monto = match
        monto = -float(monto.replace('.', '').replace(',', '.').replace('-',''))  # Convertir a número
        fecha = "20" + "-".join(reversed(fecha.split("/")))  # Convertir a formato YYYY-MM-DD
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
        monto = -float(monto.replace(',', '.').replace('-',''))  # Convertir a número
        fecha = "20" + "-".join(reversed(fecha.split("/")))  # Convertir a formato YYYY-MM-DD
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
        monto = -float(monto.replace('.', '').replace(',', '.').replace('-',''))  # Convertir a número
        fecha = "20" + "-".join(reversed(fecha.split("/")))  # Convertir a formato YYYY-MM-DD
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

# Ruta del archivo PDF
pdf_file_path = "input/pdf/202502_naranjax.pdf"

# Extraer los consumos
df_consumos = extract_consumos(pdf_file_path)

# Variables for the csv file name
csv_month = "202502"
csv_name = "_consumos__naranjax"
# Guardar en CSV
df_consumos.to_csv(f"output/csv/{csv_month}{csv_name}.csv", index=False)
print(f"Archivo '{csv_month}{csv_name}.csv' guardado con éxito.")

# Mostrar en consola
print(df_consumos)