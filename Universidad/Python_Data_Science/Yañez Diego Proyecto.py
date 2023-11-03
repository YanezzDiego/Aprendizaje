#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import mysql.connector
import numpy as np
import pandas as pd

cnx= mysql.connector.connect(
    host="localhost",
    user= "root",
    password="Diego0l22",
    database= "football_db"
)

#Cursor
cursor= cnx.cursor()

query = """ select p.playerID, p.name, a.goals,a.shots, a.assist, a.keyPasses, a.yellowCard, a.redCard, a.time, a.ownGoals, a.position from football_db.players p
inner join  football_db.appearances a
on p.playerID = a.players_playerID 
;

""" 


cursor.execute(query)

results= cursor.fetchall()

colnames= ["playerID","name", "goals","shots", "assist", "keyPasses", "yellowCard", "redCard", "time", "ownGoals", "position"]

data= pd.DataFrame(results,columns= colnames)

df=data.copy()


no_numeric= ['name' , 'position'] 
df_numeric= df.loc[:,df.columns.difference(no_numeric)]

for col_name,col in df_numeric.items():
    df[col_name]=pd.to_numeric(col,errors="coerce")
    

df["name"]=df["name"].astype(str)
df["position"]=df["position"].astype(str)


for index, row in df.iterrows():
    df.at[index, "Goles/Minuto"] = round(row["goals"] / row["time"],2)
    df.at[index, "Asistencias/Minuto"] = round(row["assist"] / row["time"],2)
    df.at[index, "PasesClave/Minuto"] = round(row["keyPasses"] / row["time"],2)
    df.at[index, "TarjetasAmarillas/Minuto"] = round(row["yellowCard"] / row["time"],2)
    df.at[index, "TarjetasRojas/Minuto"] = round(row["redCard"] / row["time"],2)

def eficiencia_disparos(row):
  if row['shots'] > 0:
    return row['goals'] / row['shots'] * 100
  else:
    return float('nan')   

df['EficienciaDisparos'] = df.apply(eficiencia_disparos, axis=1)

df= df.drop_duplicates()

df= df.dropna()

for index,row in df.iterrows():
    tupla = tuple(row)
    query = f"INSERT INTO football_db.resumen(playerID,name,goals,shots,assist,keyPasses,yellowCard,redCard,time,ownGoals,position,GolesMinuto,AsistenciasMinuto,PasesClaveMinuto,TarjetasAmarillasMinuto,TarjetasRojasMinuto,EficienciaDisparos) VALUE ({tupla[0]},'{tupla[1]}',{tupla[2]},{tupla[3]},{tupla[4]},{tupla[5]},{tupla[6]},{tupla[7]},{tupla[8]},{tupla[9]},'{tupla[10]}',{tupla[11]},{tupla[12]},{tupla[13]},{tupla[14]},{tupla[15]},{tupla[16]});"
    print("Insertando tupla: ",tupla)
    cursor.execute(query)

cnx.commit()
    
cnx.close()

