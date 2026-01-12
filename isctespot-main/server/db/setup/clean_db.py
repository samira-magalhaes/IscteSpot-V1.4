import mariadb
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Conexão com o banco usando variáveis de ambiente
db = mariadb.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "db_connector"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_DATABASE", "iscte_spot"),
    port=int(os.environ.get("DB_PORT", 3307))
)

cursor = db.cursor()

def drop_all_tables():
    """Drop all tables in a safe order (consider foreign keys)."""
    # ⚠️ Ordem importante se houver Foreign Keys entre tabelas
    tables = ['Sales', 'SupportTickets', 'Clients', 'Products', 'Users', 'Companies']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Table {table} dropped.")

    db.commit()

if __name__ == "__main__":
    drop_all_tables()
    cursor.close()
    db.close()
    print("All tables dropped and connection closed.")
