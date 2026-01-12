import mariadb
import os
import random
from dotenv import load_dotenv

# Importação dos dados fictícios
from fakes.fake_users import data as fake_users
from fakes.fake_companies import data as fake_companies
from fakes.fake_clients import data as fake_clients
from fakes.fake_products import data as fake_products
from fakes.fake_sales import data as fake_sales
from fakes.fake_tickets import data as fake_tickets

# Carregar variáveis de ambiente
load_dotenv()

try:
    # Conexão com o banco de dados
    db = mariadb.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "db_connector"),
        password=os.environ.get("DB_PASSWORD", ""),
        port=int(os.environ.get("DB_PORT", 3307)),
        database=os.environ.get("DB_DATABASE", "iscte_spot")
    )
    cursor = db.cursor()

    def insert_users():
        fake_users_tuples = [
            (
                u["Username"], u["PasswordHash"], u["Email"], u["CreatedAt"],
                u["LastLogin"], u["CompanyID"], u["ResetPassword"],
                u["CommissionPercentage"], u["LastLogout"], u["isActive"],
                u["IsAdmin"], u["IsAgent"]
            )
            for u in fake_users
        ]
        cursor.executemany("""
            INSERT INTO Users (Username, PasswordHash, Email, CreatedAt, LastLogin, 
            CompanyID, ResetPassword, CommissionPercentage, LastLogout, isActive, IsAdmin, IsAgent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, fake_users_tuples)
        db.commit()
        print(f"{len(fake_users_tuples)} utilizadores inseridos.")

    def insert_companies():
        fake_companies_tuples = [
            (
                c["CompanyID"], c["AdminUserID"], c["NumberOfEmployees"],
                c["Revenue"], c["CreatedAt"], c["CompanyName"]
            )
            for c in fake_companies
        ]
        cursor.executemany("""
            INSERT INTO Companies (CompanyID, AdminUserID, NumberOfEmployees, Revenue, CreatedAt, CompanyName)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, fake_companies_tuples)
        db.commit()
        print(f"{len(fake_companies_tuples)} empresas inseridas.")

    def insert_clients():
        fake_clients_tuples = [
            (
                cl["FirstName"], cl["LastName"], cl["Email"], cl["PhoneNumber"],
                cl["Address"], cl["City"], cl["Country"], cl["CreatedAt"], cl["CompanyID"]
            )
            for cl in fake_clients
        ]
        cursor.executemany("""
            INSERT INTO Clients (FirstName, LastName, Email, PhoneNumber, Address, City, Country, CreatedAt, CompanyID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, fake_clients_tuples)
        db.commit()
        print(f"{len(fake_clients_tuples)} clientes inseridos.")

    def insert_products():
        fake_products_tuples = [
            (
                p["ProductID"], p["CompanyID"], p["ProductName"],
                p["FactoryPrice"], p["SellingPrice"], p["CreatedAt"]
            )
            for p in fake_products
        ]
        cursor.executemany("""
            INSERT INTO Products (ProductID, CompanyID, ProductName, FactoryPrice, SellingPrice, CreatedAt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, fake_products_tuples)
        db.commit()
        print(f"{len(fake_products_tuples)} produtos inseridos.")

    def insert_sales():
        fake_sales_tuples = [
            (s["UserID"], s["ClientID"], s["ProductID"], s['Quantity'], s["SaleDate"])
            for s in fake_sales
        ]
        cursor.executemany("""
            INSERT INTO Sales (UserID, ClientID, ProductID, Quantity, SaleDate)
            VALUES (%s, %s, %s, %s, %s)
        """, fake_sales_tuples)
        db.commit()
        print(f"{len(fake_sales_tuples)} vendas inseridas.")

    def insert_tickets():
        fake_tickets_tuples = [
            (
                t["UserID"], t["Status"], t["Category"], t['Description'],
                t["Messages"], t["CreatedAt"], t["UpdatedAt"]
            )
            for t in fake_tickets
        ]
        cursor.executemany("""
            INSERT INTO SupportTickets (UserID, Status, Category, Description, Messages, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, fake_tickets_tuples)
        db.commit()
        print(f"{len(fake_tickets_tuples)} tickets inseridos.")

    # Execução por ordem de dependência
    insert_users()
    insert_companies()
    insert_products()
    insert_clients()
    insert_sales()
    insert_tickets()

    print("\nProcesso concluído com sucesso!")

except mariadb.Error as err:
    print(f"Erro durante o seeding: {err}")

finally:
    if 'db' in locals() and db:
        cursor.close()
        db.close()