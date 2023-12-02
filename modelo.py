import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.special

# N° de factura    : Invoice_ID
# Fecha de factura : Invoice_Date
# ID Cliente       : Customer_ID
# País             : Country
# Cantidad         : Quantity 
# Monto            : Amount


# Cargar el conjunto de datos
df = pd.read_csv("ventas-por-factura.csv")

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
#df['Invoice_Date'].fillna(pd.to_datetime('today'), inplace=True)

#-------------------------------------------------
#                      RFM                  
#==================================================

import datetime as dt
# Preparation of CLTV metrics

#Calcula la fecha maxima, la utlima fecha que se realizo una transacion
df["Invoice_Date"].max()   # 2021-12-09

#definimos la fecha en la que se publico el dataset
analysis_date = dt.datetime(2021,12, 10)

#definimos el dataFrame donde almacenaremos las metricas CLTV
cltv = pd.DataFrame()

#Ajustamos los datos por cliente siendo 
# Amount: La suma total del monto gastado por el cliente.
# Invoice_ID: El número único de facturas realizadas por el cliente.
# Invoice_Date: Dos funciones lambda que calculan:
#   - La antigüedad del cliente en días (días transcurridos desde la primera compra hasta la fecha de análisis).
#   - La duración de la relación del cliente en días (días transcurridos entre la primera y la última compra).  
cltv = df.groupby("Customer_ID").agg({"Amount" : lambda x : x.sum(),
                             "Invoice_ID": lambda x : x.nunique(),
                             "Invoice_Date" : [lambda x: (analysis_date - x.min()).days,
                                              lambda x: (x.max() - x.min()).days] })
cltv.columns = cltv.columns.droplevel(0) 

#renombramos las columnas de nuestras metricas
cltv.columns = ['monetary','frequency', 'T', 'recency' ]

#Aqui hacemos las compras prodemios que cada cliente realiza por transaccion
cltv["monetary"] = cltv["monetary"] / cltv["frequency"] 

#Filtramos los clientes con frecuencia con mayor a 1 
# La razón detrás de este filtrado se debe a:
#      - Estabilidad del modelo: Al centrarse en clientes que han realizado más de una compra, se busca una mayor estabilidad en las estimaciones del CLTV. Los clientes con una sola compra pueden tener comportamientos menos predecibles, y sus patrones de gasto pueden no ser representativos del valor a lo largo del tiempo.
#      - Relación comercial establecida: Los clientes que han realizado múltiples compras generalmente han establecido una relación más sólida con la empresa. Analizar el CLTV para este segmento específico puede proporcionar información más valiosa sobre el valor a largo plazo de los clientes leales.
#      - Evitar sesgos: Al filtrar clientes con una frecuencia mayor a 1, se pueden evitar sesgos en las estimaciones del CLTV que podrían surgir al incluir clientes con una única compra.
cltv.describe().T
cltv = cltv[(cltv['frequency'] > 1)]


# Convertimos los valores de dias a semanas, por lo cual dividimos entre 7
cltv["recency"] = cltv["recency"] / 7
# Lo mismo con esta columna 
cltv["T"] = cltv["T"] / 7

cltv.reset_index(inplace=True)
print(cltv.head())

from lifetimes import BetaGeoFitter 
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from scipy.special import logsumexp
from scipy.misc import logsumexp

# Establishment of BG-NBD Model and fit it

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv['frequency'],
        cltv['recency'],
        cltv['T'])


bgf.predict(4 * 3,
            cltv['frequency'],
            cltv['recency'],
            cltv['T'])

cltv["exp_sales_3_month"] = bgf.predict(4 * 3,
                                               cltv['frequency'],
                                               cltv['recency'],
                                               cltv['T'])

bgf.predict(4 * 6,
            cltv['frequency'],
            cltv['recency'],
            cltv['T'])

cltv["exp_sales_6_month"] = bgf.predict(4 * 6,
                                               cltv['frequency'],
                                               cltv['recency'],
                                               cltv['T'])
print(cltv.head(10))

# Especificamos el nombre del archivo Excel
excel_filename = "metricas_cltv.xlsx"

# Guardamos el DataFrame en un archivo Excel
cltv.to_excel(excel_filename, index=False)

print(f"El DataFrame 'cltv' se ha guardado en {excel_filename}")