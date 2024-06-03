# fastapi-jwt/main.py
import datetime
from typing import List,Union
import fastapi as _fastapi
import fastapi.security as _security
from fastapi import FastAPI, status, HTTPException, Depends
import sqlalchemy.orm as _orm
from fastapi import FastAPI, UploadFile, File
import pandas as pd
import numpy as np
import io
from fastapi.middleware.cors import CORSMiddleware
import models
import services as _services, schemas as _schemas

app = _fastapi.FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://python-fastapi-react.vercel.app","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
##############################################################User###################################################################################
@app.post("/api/users")
async def create_user(
        user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")

    user = await _services.create_user(user, db)

    return await _services.create_token(user)


@app.post("/api/token")
async def generate_token(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)


@app.get("/api/users/myprofile", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user

##############################################################Assure###################################################################################
@app.get("/api/Assure", response_model=List[_schemas.AssureBase])
async def read_Assure_list(Assure : _schemas.AssureBase = _fastapi.Depends(_services.get_db)):
    Assure_list = Assure.query(models.AssureModel).all()  # get all Assure
    return Assure_list

@app.post("/api/Assure_create",response_model=_schemas.AssureBase,status_code=status.HTTP_201_CREATED)
def create_Assure(Assure:_schemas.AssureCreat,db: _orm.Session = _fastapi.Depends(_services.get_db)):
    Assuredb = models.AssureModel(Cin=Assure.Cin,Assure_name=Assure.Assure_name)
    db.add(Assuredb)
    db.commit()
    db.refresh(Assuredb)
    return Assuredb

@app.delete("/api/Assure_delete/{Cin}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Assure(Cin: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Retrieve the Assure object from the database
    Assuredb = db.query(models.AssureModel).filter(models.AssureModel.Cin == Cin).first()

    # If Assure object does not exist, raise HTTPException with status code 404
    if not Assuredb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assure not found")

    # Delete the Assure object
    db.delete(Assuredb)
    db.commit()

    return None

@app.get("/Assure/{id}", response_model=_schemas.AssureBase)
def read_Assure(Cin: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    Assure = db.query(models.AssureModel).get(Cin)  # get item with the given id
    print(Assure)
    # check if id exists. If not, return 404 not found response
    if not Assure:
        raise HTTPException(status_code=404, detail=f"item with id {Cin} not found")

    return Assure
##########################################################Assure_insert_data_from_excel##########################################################
# @app.post("/api/insert_data_from_excel", status_code=status.HTTP_201_CREATED)
# def insert_data_from_excel(db: _orm.Session = _fastapi.Depends(_services.get_db)):
#     for index, row in data_ex.df1.iterrows():
#         cin = row['CIN']
#         assure_db = db.query(models.AssureModel).filter(models.AssureModel.Cin == cin).first()
#         if assure_db:
#             continue
#         assure_data = models.AssureModel(
#             Cin=row['CIN'],
#             Assure_name=row['Assuré']
#         )
#         Assuredb = models.AssureModel(Cin=assure_data.Cin, Assure_name=assure_data.Assure_name)
#         db.add(Assuredb)
#         db.commit()
#     return {"message": "Data inserted successfully"}
##########################################################Product##########################################################



@app.post("/api/product_create",response_model=_schemas.ProductBase,status_code=status.HTTP_201_CREATED)
def create_Assure(product: _schemas.ProductCreate,db: _orm.Session = _fastapi.Depends(_services.get_db)):
    Productdb = models.ProductModel(  Police=product.Police,
    Date_effet=product.Date_effet,
    Fractionn=product.Fractionn,
    Date_Emission=product.Date_Emission,
    Matricule=product.Matricule,
    Prime_Totale=product.Prime_Totale,
    assure_id=product.assure_id)

    # db_product = models.ProductModel(Productdb)
    db.add(Productdb)
    db.commit()
    db.refresh(Productdb)
    return Productdb


@app.get("/api/Product", response_model=List[_schemas.ProductBase])
async def read_Product_list(Product : _schemas.ProductBase = _fastapi.Depends(_services.get_db)):
    Product_list = Product.query(models.ProductModel).all()  # get all
    return Product_list



@app.delete("/api/Product_delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Assure(id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Retrieve the Product object from the database
    Productdb = db.query(models.ProductModel).filter(models.ProductModel.id == id).first()

    # If Assure object does not exist, raise HTTPException with status code 404
    if not Productdb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Delete the Product object
    db.delete(Productdb)
    db.commit()
@app.get("/Assure/{Cin}/Product/")
def get_Assure_Product(Cin: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    Assure = db.query(models.AssureModel).filter(models.AssureModel.Cin == Cin).first()
    if Assure is None:
        raise HTTPException(status_code=404, detail="Assure not found")
    return Assure.products

######################################################################
@app.get("/api/Reglement/AssureNames_Product", response_model=List[_schemas.ProductWithAssureName])
async def read_Products_with_Assure_names(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    products = db.query(models.ProductModel).all()  # Get all products
    products_with_assure_names = []
    for product in products:
        assure_data = db.query(models.AssureModel).filter(models.AssureModel.Cin == product.assure_id).first()
        product_with_assure_name = _schemas.ProductWithAssureName(
            id=product.id,
            Police=product.Police,
            Date_effet=str(product.Date_effet),
            # Add other fields from ProductModel as needed
            Assure_name=assure_data.Assure_name,
            # Acte=product.Acte,
            # Date_fin=product.Date_fin,
            Fractionn=product.Fractionn,
            # Contrat=product.Contrat,
            Date_Emission=product.Date_Emission,
            Matricule=product.Matricule,
            Attestation=product.Attestation,
            Prime_Totale=product.Prime_Totale,
            assure_id=product.assure_id)
        products_with_assure_names.append(product_with_assure_name)
    return products_with_assure_names



async def create_upload_file(file: UploadFile):
    contents = await file.read()
    return contents  # Return the file contents
##################################################################################################################################################################################################################



@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Process the uploaded file
    df1, df2 = await process_file(file)

    # Clean the DataFrames to ensure they are JSON serializable and ready for database insertion
    df1 = df1.replace([np.inf, -np.inf], np.nan).fillna(0)
    df2 = df2.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Check if the required columns exist in df1
    required_columns_df1 = {'CIN', 'Assuré'}
    if not required_columns_df1.issubset(df1.columns):
        raise HTTPException(status_code=400,
                            detail=f"Uploaded file must contain columns: {required_columns_df1} in sheet 1")

    # Check if the required columns exist in df2
    required_columns_df2 = {
        'Date Emission', 'Police', 'Date effet',  'Prime Totale', 'CIN',
        'Fractionn',  'Matricule'
    }
    if not required_columns_df2.issubset(df2.columns):
        raise HTTPException(status_code=400,
                            detail=f"Uploaded file must contain columns: {required_columns_df2} in sheet 1")

    # Insert data into AssureModel from df1
    for index, row in df1.iterrows():
        cin = row['CIN']
        assure_db = db.query(models.AssureModel).filter(models.AssureModel.Cin == cin).first()
        if assure_db:
            continue
        assure_data = models.AssureModel(
            Cin=row['CIN'],
            Assure_name=row['Assuré']
        )
        db.add(assure_data)
        db.commit()
        db.refresh(assure_data)
    # Insert data into ProductModel from df2
    for index, row in df2.iterrows():
        # Check if product already exists to avoid duplicates
        existing_product = db.query(models.ProductModel).filter(
            models.ProductModel.Date_Emission == row['Date Emission'],
            models.ProductModel.Police == row['Police'],
            models.ProductModel.Date_effet == row['Date effet'],
            models.ProductModel.Prime_Totale == row['Prime Totale'],
            models.ProductModel.assure_id == row['CIN'],
            models.ProductModel.Fractionn == row['Fractionn'],
            models.ProductModel.Matricule == row['Matricule'],
        ).first()
        if existing_product:
            continue
        product_data = models.ProductModel(
            Date_Emission=row['Date Emission'],
            Police=row['Police'],
            Date_effet=row['Date effet'],  Prime_Totale=row['Prime Totale'],
            assure_id=row['CIN'], Fractionn=row['Fractionn'],
            Matricule=row['Matricule'],
        )
        db.add(product_data)
        db.commit()
        db.refresh(product_data)

    return {"message": "Data inserted successfully"}

async def process_file(file: UploadFile):
    file_contents = await create_upload_file(file)
    # Use an in-memory buffer to read the Excel file
    buffer = io.BytesIO(file_contents)

    # Read the Excel file
    try:
        excel_file = pd.ExcelFile(buffer)
        print(f"Excel file sheets: {excel_file.sheet_names}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    # Check number of sheets in the Excel file
    if len(excel_file.sheet_names) < 1:
        raise HTTPException(status_code=400, detail="The uploaded Excel file must contain at least two sheets")

    # Read data from the first two sheets
    df1 = pd.read_excel(excel_file, sheet_name=0)  # First sheet for AssureModel
    df2 = pd.read_excel(excel_file, sheet_name=0)  # Second sheet for ProductModel

    # Ensure column names are stripped of leading/trailing spaces and are capitalized properly
    df1.columns = [col.strip() for col in df1.columns]
    df2.columns = [col.strip() for col in df2.columns]

    print(f"Sheet 1 columns: {df1.columns}")
    print(f"Sheet 2 columns: {df2.columns}")

    return df1, df2


async def create_upload_file(file: UploadFile):
    contents = await file.read()
    return contents  # Return the file contents


@app.get("/api/reglements/{id}", response_model=List[_schemas.ReglementDetail])
def read_reglement_by_cin(id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    reglements = db.query(models.ReglementModel).join(models.ProductModel).join(models.AssureModel).filter(models.ProductModel.id == id).all()

    if not reglements:
        raise HTTPException(status_code=404, detail="No reglements found for the given id")

    result = []
    for reglement in reglements:
        product = reglement.product
        assure = product.assure
        result.append(_schemas.ReglementDetail(
            cin=assure.Cin,
            nom_assure=assure.Assure_name,
            prime_totale=product.Prime_Totale,
            reste=reglement.Reste,
            matricule=product.Matricule,
            reglement=reglement.Reglement,
            type_de_reglement=reglement.Type_de_reglement
        ))

    return result


@app.post("/api/reglements/", response_model=_schemas.ReglementBase)
def create_reglement(reglement: _schemas.ReglementCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    product = db.query(models.ProductModel).filter(models.ProductModel.id == reglement.Product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

        # Fetch the last reglement for the product
    last_reglement = db.query(models.ReglementModel).filter(
        models.ReglementModel.Product_id == reglement.Product_id).order_by(models.ReglementModel.id.desc()).first()
    last_reste = last_reglement.Reste if last_reglement else product.Prime_Totale
    new_reste = last_reste - reglement.Reglement

    db_reglement = models.ReglementModel(
        Product_id=reglement.Product_id,
        Reste=new_reste,
        Garant = reglement.Garant,  

        numero = reglement.numero,
        Reglement=reglement.Reglement,
        Date_de_reglement=reglement.Date_de_reglement,
        Type_de_reglement=reglement.Type_de_reglement
    )
    db.add(db_reglement)
    db.commit()
    db.refresh(db_reglement)

    db_history = models.HistoryModel(
        assure_id=product.assure_id,
        product_id=product.id,
        reglement_id=db_reglement.id,
        action="create",
        description=f"Created reglement with Reglement: {reglement.Reglement} and Reste: {new_reste}",
        reste_amount=new_reste,        
        numero = reglement.numero,
        reglement_amount=reglement.Reglement
    )
    print(models.HistoryModel.numero)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_reglement


@app.get("/history/{cin}", response_model=List[_schemas.HistoryBase])
def get_history_by_cin(cin: str, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    history = db.query(models.HistoryModel).join(models.AssureModel).filter(models.AssureModel.Cin == cin).all()

    if not history:
        raise HTTPException(status_code=404, detail="No history found for the given CIN")
    return history

class BasicProductInfo(_schemas.ReglementDetail):
    reste: Union[None, int] = None
    reglement: Union[None, int] = None
    type_de_reglement: Union[None, str] = None


@app.get("/api/reglements/product/{product_id}",
            response_model=List[Union[_schemas.ReglementDetail, BasicProductInfo]])
def get_reglement_by_product_id(product_id: int, db: _orm.Session = Depends(_services.get_db)):
    # Fetch the product by ID
    product = db.query(models.ProductModel).filter(models.ProductModel.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="No product found for the given ID")

    # Fetch the associated assure
    assure = db.query(models.AssureModel).filter(models.AssureModel.Cin == product.assure_id).first()

    # Fetch reglements associated with the product
    reglements = db.query(models.ReglementModel).filter(models.ReglementModel.Product_id == product.id).all()

    result = []

    if not reglements:
        # If no reglements are found, return basic product information
        result.append(BasicProductInfo(
            id=product.id,
            cin=assure.Cin,
            nom_assure=assure.Assure_name,
            prime_totale=product.Prime_Totale,
            reste=None,
            matricule=product.Matricule,
            reglement=None,
            type_de_reglement=None
        ))
    else:
        for reglement in reglements:
            result.append(_schemas.ReglementDetail(
                id=product.id,
                cin=assure.Cin,
                nom_assure=assure.Assure_name,
                prime_totale=product.Prime_Totale,
                reste=reglement.Reste,
                matricule=product.Matricule,
                reglement=reglement.Reglement,
                type_de_reglement=reglement.Type_de_reglement
            ))

    return result
from fastapi import HTTPException
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/api/reglements/assure/{cin}", response_model=List[BasicProductInfo])
def get_reglement_by_cin(cin: str, db: Session = Depends(_services.get_db)):
    # Fetch the assure by CIN
    assure = db.query(models.AssureModel).filter(models.AssureModel.Cin == cin).first()

    if not assure:
        raise HTTPException(status_code=404, detail="No assure found for the given CIN")

    # Fetch the products associated with the assure
    products = db.query(models.ProductModel).filter(models.ProductModel.assure_id == assure.Cin).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found for the given CIN")

    result = []

    for product in products:
        # Return only basic product information
        result.append(BasicProductInfo(
            id=product.id,
            cin=assure.Cin,
            nom_assure=assure.Assure_name,
            prime_totale=product.Prime_Totale,
            reste=None,
            matricule=product.Matricule,
            reglement=None,
            type_de_reglement=None
        ))

    return result

