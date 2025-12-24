import mariadb
from dotenv import load_dotenv
import os # Necessário para ler variáveis de ambiente
import re  # Para validação de e-mail com Regex


load_dotenv() # Isto lê o ficheiro .env e carrega TUDO para o os.environ


class DBConnector:
  
    def __init__(self):
        # ✅ CORREÇÃO: Credenciais carregadas de variáveis de ambiente
        # Isso impede que a senha vaze se o código-fonte for exposto.
        # Use o .get() para fornecer um valor padrão seguro (ou uma exceção).
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'db_connector') # ⚠️ Evitar 'root' em produção
        self.password = os.environ.get('DB_PASSWORD') # Deixa ser None se não for definido, forçando o erro de conexão
        self.database = os.environ.get('DB_DATABASE', 'iscte_spot')
        self.port = int(os.environ.get('DB_PORT', 3306))

    # O método connect() permanece o mesmo, mas agora usa variáveis seguras.
    # ...    

    def connect(self):
        ''' Connect to database mariadb'''
        try:
            connection = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
            return connection
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return None
        

    def validate_inputs(self, query, args):
        """
        Valida e sanitiza os dados antes de processar a query.
        Retorna (True, args_limpos) ou (False, None)
        """
        try:
            # 1. Validação de IDs (Devem ser sempre Inteiros)
            # Lista de queries que esperam um ID numérico como argumento único
            queries_com_id = [
                'get_user_password', 'get_user_by_id', 'get_clients_list', 
                'get_employees_list', 'get_compnay_id_by_user', 'get_user_sales',
                'get_user_admin', 'get_user_comp_id', 'get_products_list',
                'get_company_revenue', 'get_last_3_sales', 'get_admin_tickets',
                'get_user_tickets', 'get_user_agent', 'get_ticket_by_id',
                'delete_user_by_id', 'delete_company_by_id', 'delete_client_by_id'
                'update_company_revenue', 'delete_sales_by_comp_id'            
            ]

            if query in queries_com_id:
                # Se for uma query de ID, tentamos converter para inteiro (Sanitização de tipo). 
                # Se houver texto malicioso, o int(args) vai falhar e cair no except.
                return True, int(args)

            # 2. Validação de Dicionários (Para inserts/updates)
            if isinstance(args, dict):
                # Exemplo: Validar e-mail se existir no dicionário
                if 'email' in args:
                    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    if not re.match(email_pattern, args['email']):
                        print(f"Erro: E-mail inválido - {args['email']}")
                        return False, None
                
                # Exemplo: Validar se campos numéricos são realmente números
                for field in ['comp_id', 'user_id', 'quantity', 'month', 'ticket_id', 'client_id', 'product_id']:
                    if field in args:
                        args[field] = int(args[field])
                
                # Exemplo: Sanitização de strings (Remover caracteres de comando SQL)
                for key, value in args.items():
                    if isinstance(value, str):
                        # Remove terminadores (caracteres) de comando SQL por precaução (Sanitização básica)
                        args[key] = value.replace(";", "").replace("--", "")

            return True, args

        except (ValueError, TypeError) as e:
            print(f"Erro de Validação: Dados incompatíveis para a query {query}. {e}")
            return False, None

    def execute_query(self, query, args=None):
        # --- NOVO: CAMADA DE VALIDAÇÃO ---
        is_valid, sanitized_args = self.validate_inputs(query, args)
        if not is_valid:
            print(f"ALERTA: Tentativa de query com dados inválidos: {query} | Args: {args}")
            return False
        
        args = sanitized_args # A partir daqui, os dados estão "limpos"
        # ---------------------------------

        print(f'DB query selected: {query}, args: {args}')
        connection = self.connect()
        if connection is None: return None

        cursor = connection.cursor(dictionary=True)
        # ... (segue o seu código com os blocos elif)    

    
        ''' Execute queries by query name
            query:
                READ
                    'get_user_by_name'          args:username       |       return: user id if exits if not, return false
                    'get_user_password'         args:user_id        |       return: password id if exits if not, return false
                    'get_user_by_id'            args:user_id        |       return: all parameters
                    'get_user_sales'            args:user_id        |       return: list of sales by the user
                    'get_clients_list'          args:company_id     |       return: list of clients
                    'get_employees_list'        args:company_id     |       return: list of employees
                    'get_user_admin'            args:user_id        |       return: is_admin value (True or False)
                    'get_user_comp_id'          args:user_id        |       return: comp_id
                    'get_products_list'         args:comp_id        |       return: list of products
                    'get_company_revenue'       args:comp_id        |       return: revenue
                    'get_last_3_sales'          args:user_id        |       return: list of last_3_sales
                    'get_sales_month_comp_id'   args:month,comp_id  |       return: list of sales of selected month
                    'get_costs_sales_month'     args:month,comp_id  |       return: production costs and sales revenue for given month
                    'get_admin_tickets'         args:comp_id        |       return: list of company support tickets
                    'get_user_tickets'          args:user_id        |       return: list of user support tickets
                    'get_user_agent'            args:user_id        |       return: return is_agent (True or False)
                    'get_ticket_by_id'          args:ticket_id      |       return: ticket
                    'get_agent_tickets'         args:agent token    |       return: agent tokens
                CREATE
                    'create_user_employee'      args: {username, email, company_id}
                    'create_user_admin'         args: {username, password, email}
                    'create_company'            args: {company_name, n_employees}
                    'create_client'             args: {first_name, last_name, email, phone_number, address, city, country, company_id}
                    'create_sale'               args: {client_id, user_id, product, price, quantity}
                    'create_ticket'             args: {user_id, status, description, category, messages}
                UPDATE
                    'update_user_password'      args: {user_id, new_password}
                    'update_user_comp_id'       args: {user_id, comp_id}
                    'update_products_by_comp_id args: {file, comp_id}
                    'update_company_revenue'    args: comp_id
                    'update_ticket_messages'    args: {ticket_id, message}
                    'update_ticket_status'      args: {ticket_id, status}
                DELETE
                    'delete_users_by_comp_id'   args: {user_id, company_id}
                    'delete_user_by_id'         args: user_id
                    'delete_company_by_id'      args: company_id
                    'delete_client_by_id'       args: client_id
        '''
        print(f'DB query selceted: {query}, args: {args}')
        connection = self.connect()
        if connection is None:
            return None

        cursor = connection.cursor(dictionary=True)
        result = None
        try:
            if query == 'get_user_by_name':
                cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (args,))
                result = cursor.fetchone()
                print("Result: ")
                print(result)
                try:
                    if isinstance(result, tuple):
                        result = result[0]['UserID']
                        if result == 1:
                            return True
                    else:
                        result = result["UserID"]
                        if result == 0:
                            return False
                except TypeError:
                    return 'TypeError'

            elif query == 'get_user_password':
                cursor.execute("SELECT PasswordHash FROM Users WHERE UserID = ?", (args,))
                result = cursor.fetchone()
                try:
                    if isinstance(result, tuple):
                        return result[0]['PasswordHash']
                    else:
                        return result['PasswordHash']
                except TypeError:
                    return False
            # SEGURO: Usando placeholder (?) e tupla (args,)
            elif query == 'get_user_by_id':
                cursor.execute(f"SELECT * FROM Users WHERE UserID = ?", (args,)) # Parâmetro (args,) passado separadamente
                result = cursor.fetchone()

            # SEGURO: Usando placeholder (?) e tupla (args,)
            elif query == 'get_clients_list':
                sql_query = """
                SELECT ClientID, FirstName, LastName, Email, PhoneNumber, Address, City, Country
                FROM Clients
                WHERE CompanyID = ?
                """
                cursor.execute(sql_query, (args,)) # Parâmetro (args,) passado separadamente
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_employees_list':
                cursor.execute(f"SELECT UserID, Username, Email, CommissionPercentage, isActive FROM Users WHERE CompanyID = ?", (args,))
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_compnay_id_by_user':
                cursor.execute(f"SELECT CompanyID FROM Users WHERE UserID = ?", (args,))
                result = cursor.fetchone()
                print(result)
                if isinstance(result, tuple):
                    return result[0]['CompanyID']
                else:
                    return result["CompanyID"]

            elif query == 'get_company_sales':
                cursor.execute(
                    f"""
                    SELECT Sales.SaleID, Products.ProductName, Users.Username, Clients.FirstName, Clients.FirstName, Products.SellingPrice, Sales.Quantity, Sales.SaleDate
                    FROM Sales
                    JOIN Clients ON Sales.ClientID = Clients.ClientID
                    JOIN Users ON Sales.UserID = Users.UserID
                    JOIN Products ON Sales.ProductID = Products.ProductID
                    WHERE Clients.CompanyID = {args};
                    """
                )
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_user_sales':
                # 1. Remova o 'f' antes das aspas e troque {args} por ?
                query_sql = """
                    SELECT 
                        S.SaleID,
                        U.UserName,    
                        C.FirstName,   
                        P.ProductName,
                        P.SellingPrice,
                        S.Quantity,
                        S.SaleDate
                    FROM 
                        Sales S
                    JOIN 
                        Users U ON S.UserID = U.UserID 
                    JOIN 
                        Clients C ON S.ClientID = C.ClientID 
                    JOIN 
                        Products P ON S.ProductID = P.ProductID 
                    WHERE 
                        S.UserID = ?;
                """
    
                # 2. Passe a tupla (args,) como segundo argumento. 
                # A vírgula é obrigatória para o Python entender que é uma tupla de um único valor.
                cursor.execute(query_sql, (args,))
                
                result = cursor.fetchall()
                print(result)
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_user_admin':
                cursor.execute(
                    f"""
                    SELECT IsAdmin FROM Users WHERE UserID = {args};
                    """
                )
                result = cursor.fetchone()
                print(result)
                if isinstance(result, tuple):
                    return result[0]['IsAdmin']
                else:
                    return result['IsAdmin']

            elif query == 'get_user_comp_id':
                cursor.execute(
                    f"""
                    SELECT CompanyID FROM Users WHERE UserID = {args};
                    """
                )
                result = cursor.fetchone()
                print(result)
                if isinstance(result, tuple):
                    return result[0]['CompanyID']
                else:
                    return result['CompanyID']

            elif query == 'get_products_list':
                cursor.execute(f"SELECT ProductID, ProductName, SellingPrice FROM Products WHERE CompanyID = {args}")
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_company_revenue':
                cursor.execute(f"SELECT Revenue FROM Companies WHERE CompanyID = ?", (args,))
                result = cursor.fetchone()
                if isinstance(result, tuple):
                    return result[0]
                return result['Revenue']
            
            elif query == 'get_employees_return':
                
                # 1. Removido o 'f' do início. Agora é uma string pura.
                sql = """
                    SELECT 
                        u.UserID, u.Username, u.CommissionPercentage,
                        COUNT(s.SaleID) AS total_sales,
                        SUM(s.Quantity * p.SellingPrice) AS total_sales_amount,
                        (SUM(s.Quantity * p.SellingPrice) * (u.CommissionPercentage / 100)) AS total_commission
                     FROM Users u
                    LEFT JOIN Sales s ON u.UserID = s.UserID
                    LEFT JOIN Products p ON s.ProductID = p.ProductID
                    WHERE u.CompanyID = ? 
                    AND p.CompanyID = u.CompanyID
                    AND MONTH(s.SaleDate) = ?
                    AND YEAR(s.SaleDate) = 2024
                    GROUP BY u.UserID, u.CommissionPercentage
                """
    
                # 2. Passado os valores do dicionário em uma tupla na ordem dos '?'
                # O conector enviará o comando e os dados separadamente ao banco
                cursor.execute(sql, (args['comp_id'], args['month']))
                result = cursor.fetchall()
                # Format the result into a list of dictionaries
                employee_sales_data = []
                print(f'Result: {result}')
                for row in result:
                    employee_sales_data.append({
                        "UserID": row['UserID'],
                        "Username": row['Username'],
                        "CommissionPercentage": row['CommissionPercentage'],
                        "TotalSales": row['total_sales'],
                        "TotalSalesAmount": row['total_sales_amount'],
                        "TotalCommission": row['total_commission']
                    })

                return employee_sales_data

            elif query == 'get_last_3_sales':
                cursor.execute(
                    f"""
                    SELECT 
                        S.SaleID,
                        U.UserName,    
                        C.FirstName,   
                        P.ProductName,
                        P.SellingPrice,
                        S.Quantity,
                        S.SaleDate
                    FROM 
                        Sales S
                     JOIN
                        Users U ON S.UserID = U.UserID       -- Join the Users table to get UserName
                    JOIN 
                        Clients C ON S.ClientID = C.ClientID -- Join the Clients table to get ClientName
                    JOIN 
                        Products P ON S.ProductID = P.ProductID -- Join the Products table to get ProductName
                    WHERE 
                        S.UserID = {args}
                  	ORDER BY
                        S.SaleDate DESC
                   LIMIT 3;
                    """
                )
                result = cursor.fetchall()
                print(result)
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_sales_month_comp_id':
                cursor.execute(
                    """
                    SELECT 
                        Sales.SaleID,
                        Sales.UserID,
                        Sales.ClientID,
                        Sales.ProductID,
                        Sales.Quantity,
                        Sales.SaleDate
                    FROM 
                        Sales
                    JOIN 
                        Users ON Sales.UserID = Users.UserID
                    WHERE 
                        Users.CompanyID = ?
                        AND MONTH(Sales.SaleDate) = ?
                        AND YEAR(Sales.SaleDate) = 2024;
                    """,
                    (args['comp_id'], args['month'])
                )
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            # SEGURO: Usando múltiplos placeholders (?)
            elif query == 'get_costs_sales_month':
                sql_query = """
                SELECT 
                    SUM(Products.SellingPrice * Sales.Quantity) AS TotalSellingPrice,
                    SUM(Products.FactoryPrice * Sales.Quantity) AS TotalFactoryPrice
                FROM 
                    Sales
                JOIN 
                    Products ON Sales.ProductID = Products.ProductID
                WHERE 
                    Products.CompanyID = ? # ✅ Placeholder para args['comp_id']
                    AND MONTH(Sales.SaleDate) = ? # ✅ Placeholder para args['month']
                    AND YEAR(Sales.SaleDate) = 2024;
                """
                # Tupla de argumentos na ordem exata dos placeholders
                query_args = (args['comp_id'], args['month'])
                cursor.execute(sql_query, query_args)
                result = cursor.fetchone()
                print(result)
                try:
                    if isinstance(result, tuple):
                        return result[0]
                    else:
                        return result
                except TypeError:
                    return False

            elif query == 'get_admin_tickets':
                # 1. Remova o 'f' (f-string) e substitua {args} por ?
                sql = """
                    SELECT 
                        st.TicketID,
                        st.UserID,
                        u.CompanyID,
                        st.Status,
                        st.Category,
                        st.Description,
                        st.Messages,
                        st.CreatedAt,
                        st.UpdatedAt
                    FROM 
                        SupportTickets st
                    JOIN 
                        Users u ON st.UserID = u.UserID
                    WHERE 
                        u.CompanyID = ?;
                """
    
                # 2. Passe 'args' dentro de uma tupla (args,) no execute
                cursor.execute(sql, (args,))

                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False

            elif query == 'get_user_tickets':
                cursor.execute(
                    f"""
                    SELECT 
                        TicketID,
                        UserID,
                        Status,
                        Category,
                        Description,
                        Messages,
                        CreatedAt,
                        UpdatedAt
                    FROM 
                        SupportTickets st
                    WHERE 
                        UserID = {args};
                    """
                )
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False
            
            elif query == 'get_user_tickets':
                cursor.execute(
                    f"""
                    SELECT 
                        
                    FROM 
                        SupportTickets st
                    WHERE 
                        UserID = {args};
                    """
                )
                result = cursor.fetchall()
                if isinstance(result, list):
                    return result
                else:
                    return False
            
            elif query == 'get_user_agent':
                cursor.execute(
                    f"""
                    SELECT IsAgent FROM Users WHERE UserID = {args};
                    """
                )
                result = cursor.fetchone()
                print(result)
                try:
                    return result['IsAgent'] == 1
                except TypeError:
                    return False
            
            elif query == 'get_ticket_by_id':
                cursor.execute(
                    f"""
                    SELECT * FROM SupportTickets WHERE TicketID = {args};
                    """
                )
                result = cursor.fetchone()
                print(result)
                try:
                    if isinstance(result, tuple):
                        return result[0]
                    else:
                        return result
                except TypeError:
                    return False

            elif query == 'get_agent_tickets':
                cursor.execute('SELECT * From SupportTickets')
                result = cursor.fetchall()
                print(result)
                if isinstance(result, list):
                    return result
                else:
                    return False
                
            elif query == 'create_user_employee':
                cursor.execute(
                    "INSERT INTO Users (Username, PasswordHash, Email, CompanyID, CommissionPercentage, CreatedAt) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (args['username'], 'T3MP-password-32',args['email'], args['comp_id'], 5)
                )
                connection.commit()
                result = cursor.lastrowid
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result

            elif query == 'create_user_admin':
                cursor.execute(
                    "INSERT INTO Users (Username, PasswordHash, Email, IsAdmin, CreatedAt) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);",
                    (args['username'], args['password'],args['email'], args['is_admin'])
                )
                connection.commit()
                result = cursor.lastrowid
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result

            elif query == 'create_company':
                cursor.execute(
                    "INSERT INTO Companies (CompanyName, NumberOfEmployees, AdminUserID, Revenue) VALUES (?, ?, ?, ?)",
                    (args['comp_name'], args['num_employees'], args['user_id'], 0)
                )
                connection.commit()
                result = cursor.lastrowid
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result

            elif query == 'create_client':
                cursor.execute(
                    "INSERT INTO Clients (FirstName, LastName, Email, PhoneNumber, Address, City, Country, CompanyID, CreatedAt) VALUES (?, ?, ?, ?, ?, ? ,?, ?, CURRENT_TIMESTAMP)",
                    (args['first_name'], args['last_name'], args['email'], args['phone_number'], args['address'], args['city'], args['country'], args['comp_id'])
                )
                connection.commit()
                result = cursor.lastrowid
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result
            
            elif query == 'create_sale':
                cursor.execute(
                    "INSERT INTO Sales (UserID, ClientID, ProductID, Quantity, SaleDate) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (args['user_id'], args['client_id'], args['product_id'], args['quantity'])
                )
                connection.commit()
                result = cursor.lastrowid
                print(result)
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result
            
            elif query == 'create_ticket':
                cursor.execute(
                    "INSERT INTO SupportTickets (UserID, Status, Category, Description, Messages, CreatedAt) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (args['user_id'], args['status'], args['category'], args['description'], args['messages'])
                )
                connection.commit()
                result = cursor.lastrowid
                if isinstance(result, tuple):
                    return result[0]
                else:
                    return result

            elif query == 'update_user_password':
                cursor.execute(
                    "UPDATE Users SET PasswordHash = ? WHERE UserID = ?;",
                    (args["new_password"], args["user_id"])
                )
                connection.commit()
                result = cursor.rowcount
                if isinstance(result, tuple):
                    result = result[0]
                if cursor.rowcount > 0:
                    return True
                else:
                    return False

            elif query == 'update_user_comp_id':
                cursor.execute(
                    "UPDATE Users SET CompanyID = ? WHERE UserID = ?;",
                    (args["comp_id"], args["user_id"])
                )
                connection.commit()
                result = cursor.rowcount
                if isinstance(result, tuple):
                    result = result[0]
                if cursor.rowcount > 0:
                    return True
                else:
                    return False

            # SEGURO: Usando placeholders e lógica mais limpa
            elif query == 'update_user_activity':
                user_id = args['user_id']
                if args['active']:
                    # Se for True, atualiza LastLogin e isActive
                    sql_query = "UPDATE Users SET LastLogin = CURRENT_TIMESTAMP, isActive = True WHERE UserID = ?"
                    cursor.execute(sql_query, (user_id,))
                else:
                    # Se for False, atualiza LastLogout e isActive
                    sql_query = "UPDATE Users SET LastLogout = CURRENT_TIMESTAMP, isActive = False WHERE UserID = ?"
                    cursor.execute(sql_query, (user_id,))
                connection.commit()
                result = cursor.rowcount
                if isinstance(result, tuple):
                    result = result[0]
                return result

            elif query == 'update_products_by_comp_id':
                cursor.execute(
                    f"""
                    DELETE FROM Products WHERE CompanyID = {args['comp_id']}
                    """
                )

                insert_query = """
                    INSERT INTO Products (ProductID, CompanyID, ProductName, FactoryPrice, SellingPrice, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, ?)
                """

                for index, row in args['file'].iterrows():
                    cursor.execute(insert_query, (row['ProductID'], args['comp_id'], row['ProductName'],row['FactoryPrice'], row['SellingPrice'],  row['CreatedAt']))
                
                connection.commit()
                return True

            elif query == 'update_company_revenue':

                cursor.execute(
                    f"""
                    SELECT SUM(s.Quantity * p.SellingPrice) AS total_sales
                    FROM Sales s
                    JOIN Products p ON s.ProductID = p.ProductID
                    JOIN Users u ON s.UserID = u.UserID
                    WHERE u.CompanyID = {args};
                    """
                )
                result = cursor.fetchone()
                if isinstance(result, dict):
                    result = result['total_sales']

                cursor.execute(
                    f"""
                    UPDATE Companies
                    SET Revenue = {result}
                    WHERE CompanyID = {args}
                    """
                )
                connection.commit()
                affected_rows = cursor.rowcount
                return affected_rows > 0
            
            elif query == 'update_ticket_messages':
                message = args["message"]
                username = args['username']
                ticket_id = args['ticket_id']
                new_status = 'Waiting for customer' if args['is_agent'] else 'Waiting for support'
                
                # Use placeholders (%s) for parameters
                cursor.execute(
                    """
                    UPDATE SupportTickets
                    SET 
                        Messages = JSON_ARRAY_APPEND(
                            IFNULL(Messages, JSON_ARRAY()), '$', JSON_OBJECT('Username', %s, 'MessageText', %s)
                        ),
                        UpdatedAt = CURRENT_TIMESTAMP,
                        Status = %s
                    WHERE TicketID = %s;
                    """, (username, message, new_status, ticket_id)
                )
                
                connection.commit()
                affected_rows = cursor.rowcount
                return affected_rows >= 0

            elif query == 'update_ticket_status':
                
                cursor.execute(
                    """
                    UPDATE SupportTickets
                    SET Status = %s, UpdatedAt = CURRENT_TIMESTAMP
                    WHERE TicketID = %s""",
                    (args['status'], args['ticket_id'])
                )
                connection.commit()
                affected_rows = cursor.rowcount
                return affected_rows >= 0
            
            elif query == 'delete_sales_by_comp_id':
                cursor.execute(
                    f"""
                    DELETE FROM sales
                    WHERE UserID IN (
                        SELECT UserID
                        FROM users
                        WHERE CompanyID = {args}
                    );

                    """)
                connection.commit()
                result = cursor.rowcount
                return True
            
            elif query == 'update_seller_commission':
                # 1. String pura sem 'f', usando '?' como placeholders
                sql = "UPDATE Users SET CommissionPercentage = ? WHERE UserID = ?"

                # 2. Valores passados separadamente como uma tupla
                cursor.execute(sql, (args['new_commission'], args['seller_id']))                
                connection.commit()
                result = cursor.rowcount
                print(result)
                if isinstance(result, tuple):
                    result = result[0]
                return result

            elif query == 'delete_sales_by_comp_id':
                cursor.execute(
                    f"""
                    DELETE FROM sales
                    WHERE UserID IN (
                        SELECT UserID
                        FROM users
                        WHERE CompanyID = {args}
                    );

                    """)
                connection.commit()
                result = cursor.rowcount
                print('Deleting Sales')
                print(result)
                return True
            
            elif query == 'delete_products_by_comp_id':
                cursor.execute(f"DELETE FROM Products WHERE CompanyID = {args}")
                connection.commit()
                result = cursor.rowcount
                return True
            
            elif query == 'delete_users_by_comp_id':
                cursor.execute(f"DELETE FROM Users WHERE CompanyID = {args}")
                connection.commit()
                result = cursor.rowcount
                return True

            elif query == 'delete_user_by_id':
                cursor.execute("DELETE FROM Users WHERE UserID = ?", (args,))
                connection.commit()
                result = cursor.rowcount
                print(result)
                if result > 0:
                    return True
                else:
                    return False

            elif query == 'delete_company_by_id':
                cursor.execute(f"DELETE FROM Companies WHERE CompanyID = ?", (args,))
                connection.commit()
                result = cursor.rowcount
                if isinstance(result, tuple):
                    result = result[0]
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
            # SEGURO: Usando placeholder (?) e tupla (args,)
            elif query == 'delete_client_by_id':
                cursor.execute(f"DELETE FROM Clients WHERE ClientID = ?", (args,)) # Parâmetro (args,) passado separadamente
                connection.commit()
                result = cursor.rowcount
                if isinstance(result, tuple):
                    result = result[0]
                if cursor.rowcount > 0:
                    return True
                else:
                    return False

        except mariadb.Error as e:
            print(f"Error: {e}")
            result = None
        finally:
            cursor.close()
            connection.close()
        return result
