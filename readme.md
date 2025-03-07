# What's the intention of this repo? 
It returns the raw information from bank account resumes by month. For instance, if you have a VISA credit card, you can download as a PDF the resume of a month, and this will create a CSV with information for further analysis. <br />
The intention is to automate expenses, so you can use the CSV(s) for dashboard's creation.
<br />
# Libraries to install
- [Pandas](https://pandas.pydata.org)
```pip install pandas```
- [pdfplumber](https://python.langchain.com/docs/integrations/document_loaders/pdfplumber/)
```pip instal pdfplumber```
- [openpyxl](https://pypi.org/project/openpyxl/)
```pip install openpyxl```
# How to use scripts 
I am creating one script per credit card and entity. 
## Entities:
- NaranjaX
- Galicia VISA
- Galicia MasterCard
- Mercado Pago (Transacciones). [Official documentation](https://www.mercadopago.com.ar/developers/es/docs/checkout-api/additional-content/reports/account-money/introduction)
### Additional considerations
Please, have in mind that the way I am identifying rows within a PDF is based on REGEX functions. It means that the each script will work only for a specific type of PDF structure. <br />
Feel free to clone the repository and modify it accordingly. 
<br />
Please, have in mind that some line items could be missing due to the REGEX function and how I am detecting rows. Double check JIC. 