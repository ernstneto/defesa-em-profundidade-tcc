import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

# As mesmas credenciais do banco de dados que usamos no docker-compose
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/search_flask')
def search():
    query = request.args.get('q', '')
    html_output = "<h1>Busca Flask</h1>"
    
    if not query:
        return html_output + "<p>Nenhum autor para buscar.</p>"
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # A mesma vulnerabilidade pura
        sql_query = f"SELECT author, text FROM comments_comment WHERE author = '{query}'"
        print("!!! FLASK DEBUG: Executando query:", sql_query)
        
        cur.execute(sql_query)
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        html_output += "<h2>Resultados:</h2>"
        if not results:
            html_output += "<p>Nenhum comentário encontrado.</p>"
        else:
            for row in results:
                # row[0] é o autor, row[1] é o texto
                html_output += f"<p><b>{row[0]}</b>: {row[1]}</p>"
                
    except Exception as e:
        print("!!! FLASK DATABASE ERROR:", e)
        html_output += f"<p>Erro no banco de dados: {e}</p>"

    return html_output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)