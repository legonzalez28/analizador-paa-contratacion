import sqlite3, json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('paa.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analisis_paa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            dependencia TEXT,
            objeto TEXT,
            valor REAL,
            mes TEXT,
            codigo_unspsc TEXT,
            modalidad TEXT,
            riesgos TEXT,
            motor_ia TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_analisis(necesidad, resultado):
    conn = sqlite3.connect('paa.db')
    conn.execute(
        'INSERT INTO analisis_paa VALUES (NULL,?,?,?,?,?,?,?,?,?)',
        (
            datetime.now().isoformat(),
            necesidad.dependencia,
            necesidad.objeto,
            necesidad.valor,
            necesidad.mes,
            resultado.get('codigo_unspsc'),
            resultado.get('modalidad_recomendada'),
            json.dumps(resultado.get('riesgos'), ensure_ascii=False),
            resultado.get('motor_ia')
        )
    )
    conn.commit()
    conn.close()