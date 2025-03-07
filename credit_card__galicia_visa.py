import pdfplumber
import re
import pandas as pd

csv_month = "202503" # <<<<----- PLEASE, MODIFY IT ACCORDINGLY 
reported_month = '2025-03-01' # <<<<----- PLEASE, MODIFY IT ACCORDINGLY 
csv_name = "__galicia_visa" 
input_pdf_file_path = f"input/pdf/{csv_month}{csv_name}.pdf" 
output_pdf_file_path = f"output/csv/{csv_month}{csv_name}.csv" 

def extract_consumos_galicia_visa(pdf_path):
    consumos = []
    
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # Normalizar texto eliminando espacios dobles y caracteres especiales
    text = re.sub(r'\s+', ' ', text)
    
    # Extraer la sección "DETALLE DEL CONSUMO"
    match = re.search(r"DETALLE DEL CONSUMO (.*?) TOTAL A PAGAR", text, re.DOTALL)
    if match:
        consumos_text = match.group(1)
    else:
        raise ValueError("No se encontró la sección 'DETALLE DEL CONSUMO'")
    
    # Eliminar valores dentro de paréntesis
    consumos_text = re.sub(r"\(\s*\d{1,3},\d{2}\s*\)", "", consumos_text)
    # Eliminar montos adicionales después de $ SOLO para casos con 'PAG.MIN.ANTERIOR'
    consumos_text = re.sub(r"(PAG\.MIN\.ANT\.ANTER\.|PAG\.MIN\.ANTERIOR)\s+\$\s*\d{1,3}(?:\.\d{3})*,\d{2}\s+", r"\1 $ ", consumos_text)
    
    # Eliminar el monto incorrecto después del % en 'DB IVA', conservando el último valor correcto
    consumos_text = re.sub(r"(DB IVA\s+\$\s*\d{1,3}(?:\.\d{3})*,\d{2}\s*\d{1,2}%\s+)\d{1,3}(?:\.\d{3})*,\d{2}\s+(\d{1,3}(?:\.\d{3})*,\d{2})", r"DB IVA \1 \2", consumos_text)
    
    # Patrón mejorado para capturar transacciones
    pattern_transacciones = re.findall(
        r"(\d{2}-\d{2}-\d{2})\s+(.+?)\s+\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})", 
        consumos_text
    )

       # Función para asignar subcategoría en base a detalles
    def assign_subcategory(details):
        if "EXPRESS" in details.upper() or "RES" in details.upper() or "DAR" in details.upper() or "COTO" in details.upper():
            return "grocery"
        elif "FARMACITY" in details.upper():
            return "pharmacy"
        elif "OSDE" in details.upper():
            return "health_care"
        elif "MANTENIMIENTO" in details.upper() or "IMPUESTO" in details.upper() or "IVA" in details.upper() or "CUENTA PREF" in details.upper() or "INTERES" in details.upper() or "PERCEP" in details.upper() or "PAG.MIN" in details.upper() or "DB.RG" in details.upper():
            return "bank_account_fees"
        elif "OPENAI" in details.upper() or "GRID" in details.upper():
            return "personal"
        elif "MERPAGO MERCADOLIBRE" in details.upper():
            return "online_shopping"
        elif "METROGAS" in details.upper() or "YPF" in details.upper() or "EDENOR" in details.upper() or "PERSONALFLOW" in details.upper():
            return "services"
        elif "UBER" in details.upper() or "CABIFY" in details.upper() or "DIDI" in details.upper() or "TAXI" in details.upper() or "PASAJESCDP" in details.upper():
            return "transportation"
        else:
            return "other"
    
    # Procesar transacciones
    for i, match in enumerate(pattern_transacciones):
        fecha, detalle, monto = match
        day, month, year = fecha.split("-")
        formatted_date = f"20{year}-{month}-{day.zfill(2)}"
        
        moneda = "USD" if "USD" in detalle.upper() else "ARS"
        monto_final = float(monto.replace('.', '').replace(',', '.'))
        
        consumos.append({
            "report_month": reported_month,
            "event_date": formatted_date,
            "details": detalle.strip(),
            "amount": monto_final,
            "currency": moneda,
            "category": "credit_card_galicia_visa", 
            "subcategory": assign_subcategory(detalle)
        })
    
    df = pd.DataFrame(consumos)
    return df

df_consumos = extract_consumos_galicia_visa(input_pdf_file_path)

# Guardar en CSV
df_consumos.to_csv(output_pdf_file_path, index=False)
print(f"Archivo '{csv_month}{csv_name}.csv' guardado con éxito.")

print(df_consumos)