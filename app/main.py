from typing import Union
from pydantic import BaseModel
import pandas as pd
import os
import datetime, secrets

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from fastapi import FastAPI

app = FastAPI()


username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
csv = pd.read_csv("/files/data.csv", sep=";")
token = None
tokenCreated = datetime.date(1980,1,1)

class Prijava(BaseModel):
    uporabniskoIme: str
    geslo: str

class Zeton(BaseModel):
    zeton: str

class PridobiPodatki(BaseModel):
    zeton: str
    maticna: int
    davcna: str | None = None
    naziv: str | None = None
    leto: int
    mesec: int
    energent: str

class Podatki(BaseModel):
    skupnaKolicina: float
    povprecnaCenaNaEnoto: float

@app.post("/Dobavitelj/Prijava")
def prijava(prj: Prijava) -> Zeton:
    if prj.uporabniskoIme == username and prj.geslo == password:
        global token
        token = secrets.token_urlsafe(30)
        global tokenCreated
        tokenCreated = datetime.datetime.now()
        return {
            "zeton": token
        }
    else:
        raise HTTPException(status_code=401, detail="Wrong username or password")

@app.post("/Dobavitelj/PridobiPodatke")
def read_item(podatki: PridobiPodatki) -> Podatki:
    if not (podatki.zeton == token and (datetime.datetime.now() - tokenCreated).total_seconds() < 3600):
        raise HTTPException(status_code=401, detail="Wrong or expired token")
    data = csv[(csv.maticna == podatki.maticna)&(csv.leto == podatki.leto)&(csv.mesec == podatki.mesec)&(csv.energent == podatki.energent)]
    print(len(data))
    if len(data) > 0:
        return {
            "skupnaKolicina": float(data.iloc[0]["skupnaKolicina"]),
            "povprecnaCenaNaEnoto": float(data.iloc[0]["povprecnaCenaNaEnoto"])
        }
    else:
        raise HTTPException(status_code=404, detail="No such data in database")
