import mariadb
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Conexão com o banco usando variáveis de ambiente
db = mariadb.connect(
    host=os.environ.get("DB_HOST", "mariadb"),
    user=os.environ.get("DB_USER", "db_connector"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_DATABASE", "iscte_spot"),
    port=int(os.environ.get("DB_PORT", 3306))
)

cursor = db.cursor()

def drop_all_tables():
    """Drop all tables safely by disabling foreign key checks temporarily."""
    # ⚠️ Desativa checks de foreign key
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    tables = ['Sales', 'SupportTickets', 'Clients', 'Products', 'Users', 'Companies']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Table {table} dropped.")

    # ✅ Reativa checks de foreign key
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    db.commit()

if __name__ == "__main__":
    drop_all_tables()
    cursor.close()
    db.close()
    print("All tables dropped and connection closed.")
