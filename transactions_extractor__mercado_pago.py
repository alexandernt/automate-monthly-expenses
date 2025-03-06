import pandas as pd
import os


# input_file = "input/csv/202502_mp_transactions.csv"
input_file = "input/csv/202502_transactions__mercado_pago.xlsx"
output_csv_month = "202502"
output_file = f"output/csv/{output_csv_month}_transactions__mercado_pago.csv"
reporting_month = "202502"

# import pandas as pd
# import os

# # Ruta del archivo XLSX
# input_file = "/mnt/data/202502_mp_transactions.xlsx"
# output_file = "/mnt/data/filtered_transactions.csv"

# Cargar el XLSX con manejo de errores
df = pd.read_excel(input_file, engine="openpyxl")

# Filtrar solo las columnas necesarias
columns_needed = ["TRANSACTION_CURRENCY", "TRANSACTION_AMOUNT", "ORIGIN_DATE", "STORE_NAME", "SALE_DETAIL"]
df = df[columns_needed]

# Filtrar solo las transacciones con monto negativo
df = df[df["TRANSACTION_AMOUNT"] < 0]

# Crear nuevas columnas
df["reporting_month"] = "2025-02-01"  # Puedes hacer que esto sea dinámico si se necesita
df["event_date"] = pd.to_datetime(df["ORIGIN_DATE"], errors='coerce').dt.date
df["details"] = df["STORE_NAME"].astype(str).str.replace('"', '') + " " + df["SALE_DETAIL"].astype(str).str.replace('"', '')
df["amount"] = df["TRANSACTION_AMOUNT"].abs()
df["currency"] = df["TRANSACTION_CURRENCY"]
df["category"] = "transactions_mercado_pago"

# Función para asignar sub-categoría
def assign_subcategory(details):
    details = details.upper()
    if any(x in details for x in ["EXPRESS", "RES", "DAR", "MARKET JURAMENTO", "COTO"]):
        return "grocery"
    elif "FARMACITY" in details:
        return "pharmacy"
    elif "CAFE" in details:
        return "coffee"
    elif "STRANGE" in details:
        return "restaurant_bar"
    if any(x in details for x in ["BICI", "PHOTO"]):
        return "personal"
    if any(x in details for x in ["MORADAS", "RAPPI", "PEDIDO" , "DADA"]):
        return "delivery"
    else:
        return "other"


# Asignar categoría
# df["category"] = df["details"].apply(assign_category)
df["subcategory"] = df["details"].apply(assign_subcategory)

# Seleccionar las columnas finales
final_columns = [
    "reporting_month", 
    "event_date", 
    "details", 
    "amount", 
    "currency", 
    "category",
    "subcategory"
]
df = df[final_columns]

# Guardar el resultado
df.to_csv(output_file, index=False)

print(f"Archivo procesado y guardado en: {output_file}")