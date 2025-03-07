import pdfplumber
import re
import pandas as pd

csv_month = "202503" # <<<<----- PLEASE, MODIFY IT ACCORDINGLY 
report_month = "2025-03-01" # <<<<----- PLEASE, MODIFY IT ACCORDINGLY
csv_name = "__galicia_mastercard"
input_pdf_file_path = f"input/pdf/{csv_month}{csv_name}.pdf" 
output_pdf_file_path = f"output/csv/{csv_month}{csv_name}.csv" 

def extract_consumos_galicia_mastercard(pdf_path):
    consumos = []

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Mapeo de meses en español a números
    month_map = {
        "Ene": "01", "Feb": "02", "Mar": "03", "Abr": "04", "May": "05", "Jun": "06",
        "Jul": "07", "Ago": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dic": "12"
    }

    # Buscar todas las transacciones sin dividir por secciones
    pattern_transacciones = re.findall(
        r"(\d{2}-[A-Za-z]{3}-\d{2})\s+([\w\s\*/\d\.\-]+?)\s+\d+\s+(\d{1,3}(?:\.\d{3})*,\d{2}|\d{1,3},\d{3}\.\d{2})", text
    )

    # Extraer la sección de fees entre "SUBTOTAL" y "TOTAL A PAGAR"
    match_fees = re.search(r"SUBTOTAL\s+[\d\.,]+\s+0,00\s*(.*?)TOTAL A PAGAR", text, re.DOTALL)
    if match_fees:
        fees_text = match_fees.group(1)
        pattern_fees = re.findall(
            r"([\w\s\.%]+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})", fees_text
        )
    else:
        pattern_fees = []

    # Función para asignar subcategoría en base a detalles
    def assign_subcategory(details):
        if "EXPRESS" in details.upper() or "RES" in details.upper() or "DAR" in details.upper() or "MARKET JURAMENTO" in details.upper() or "COTO" in details.upper():
            return "grocery"
        elif "FARMACITY" in details.upper():
            return "pharmacy"
        elif "OSDE" in details.upper():
            return "health_care"
        elif "MANTENIMIENTO" in details.upper():
            return "bank_account_fees"
        elif "OPENAI" in details.upper() or "GRID" in details.upper():
            return "personal"
        elif "MERPAGO MERCADOLIBRE" in details.upper():
            return "online_shopping"
        elif "METROGAS" in details.upper() or "YPF" in details.upper() or "EDENOR" in details.upper() or "PERSONALFLOW" in details.upper():
            return "services"
        elif "UBER" in details.upper() or "CABIFY" in details.upper() or "DIDI" in details.upper() or "TAXI" in details.upper() or "PASAJESCDP" in details.upper():
            return "transportation"
        elif "ESTUDIOG" in details.upper():
            return "contador"
        else:
            return "other"

    # Procesar transacciones normales
    for match in pattern_transacciones:
        fecha, detalle, monto = match

        # Convertir fecha al formato YYYY-MM-DD
        day, month_str, year = fecha.split("-")
        month = month_map.get(month_str, "01")
        formatted_date = f"20{year}-{month}-{day.zfill(2)}"

        # Determinar si el monto es en ARS o USD basándose en el formato
        if re.match(r"^\d{1,3}(?:\.\d{3})*,\d{2}$", monto):
            moneda = "ARS"
            monto = float(monto.replace('.', '').replace(',', '.'))
        else:
            moneda = "USD"
            monto = float(monto.replace(',', '.'))

        consumos.append({
            "report_month": report_month,
            "event_date": formatted_date,
            "details": detalle.strip(),
            "amount": monto,
            "currency": moneda,
            "category": "credit_card_galicia_mastercard",
            "subcategory": assign_subcategory(detalle)
        })

    # Procesar fees
    for detalle, monto in pattern_fees:
        monto = float(monto.replace('.', '').replace(',', '.'))
        consumos.append({
            "report_month": report_month,
            "event_date": report_month,  # Se usa la fecha de reporte porque los fees no tienen fecha específica
            "details": detalle.strip(),
            "amount": monto,
            "currency": "ARS",
            "category": "credit_card_galicia_mastercard",
            "subcategory": "bank_account_fees"
        })

    df = pd.DataFrame(consumos)
    return df

df_consumos = extract_consumos_galicia_mastercard(input_pdf_file_path)

# Guardar en CSV
df_consumos.to_csv(output_pdf_file_path, index=False)
print(f"Archivo '{csv_month}{csv_name}.csv' guardado con éxito.")
print(df_consumos)