import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# N° de factura    : Invoice_ID
# Fecha de factura : Invoice_Date
# ID Cliente       : Customer_ID
# País             : Country
# Cantidad         : Quantity 
# Monto            : Amount


# Cargar el conjunto de datos
df = pd.read_excel("ventas-por-factura.xlsx")

# Explorar los primeros registros del DataFrame
print(df.head())

# Verificar la información del DataFrame
print(df.info())

#Modificando el nombre de las columnas
df.columns = ["Invoice_ID","Invoice_Date", "Customer_ID","Country",
            "Quantity","Amount"]

# Limpieza de datos (manejar valores nulos, duplicados, etc.)
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Separamos la varable fecha del time
df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"]).dt.date

# Convertimos el objeto Invoice_date a tipo datatime
df["Invoice_Date"] = pd.to_datetime(df["Invoice_Date"])

#  convertir el objeto monto en tipo flotante
df["Amount"] = df["Amount"].str.replace(",",".").astype(float)


# Convertir la columna "Invoice_ID" a tipo de datos string
df["Invoice_ID"] = df["Invoice_ID"].astype(str)

# Filtrar las filas donde "Invoice_ID" no contiene la letra "C"
df = df[~df["Invoice_ID"].str.contains("C")]

#Sacar las facturas de devolucion ( las negativas )
df[df["Amount"] == 0.0].shape 
df = df[df["Amount"] > 0]

# Imputar valores nulos en 'Invoice_Date'
df['Invoice_Date'].fillna(pd.to_datetime('today'), inplace=True)

#-------------------------------------------------
#                      RFM                  
#==================================================

# Calcular Frequency y Monetary
rfm_table = df.groupby('Customer_ID').agg({
    'Invoice_Date': 'max',
    'Invoice_ID': 'count',
    'Amount': 'sum'
})

#Definimos las tablas de nuestro RFM
rfm_table.columns = ['Recency', 'Frequency', 'Monetary']

# Calcular Recency 
df['Recency'] = pd.to_datetime('today') - df.groupby('Customer_ID')['Invoice_Date'].transform('max')

#Convertimos las fechas de tipo datatime a tipo int - 673 al dia 24 de Diciembre de 2023
rfm_table['Recency'] = (pd.to_datetime('today') - rfm_table['Recency']).dt.days.astype(int) - 673

# Con esto generamos la ganancia promedio por compra ya que de lo contrario muestra el total de su frecuencia
rfm_table["Monetary"] = rfm_table["Monetary"] / rfm_table["Frequency"] 

# Calcular cuartiles para cada métrica RFM
rfm_table['Recency_Quartile'] = pd.qcut(rfm_table['Recency'], q=4, labels=False)
rfm_table['Frequency_Quartile'] = pd.qcut(rfm_table['Frequency'], q=[0, 0.25, 0.5, 0.75, 1.0], labels=False, duplicates='drop')
rfm_table['Monetary_Quartile'] = pd.qcut(rfm_table['Monetary'], q=4, labels=False)

# Calcular la puntuación RFM total
rfm_table['RFM_Score'] = rfm_table['Recency_Quartile'] + rfm_table['Frequency_Quartile'] + rfm_table['Monetary_Quartile']



# Visualizar la distribución de puntuaciones RFM
sns.histplot(rfm_table['RFM_Score'], bins=range(5), kde=True)
plt.title('Distribución de Puntuaciones RFM')
plt.xlabel('Puntuación RFM')
plt.ylabel('Frecuencia')
#Muestra al grafica RFM
plt.show()

    
print(rfm_table.info())
print(rfm_table.head())


