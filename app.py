from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# Mapa de dias da semana
DIAS_SEMANA = {
    0: 'Domingo',
    1: 'Segunda-feira',
    2: 'Terça-feira',
    3: 'Quarta-feira',
    4: 'Quinta-feira',
    5: 'Sexta-feira',
    6: 'Sábado'
}

# Banco de dados
DATABASE = 'agendamentos.db'


def init_db():
    """Inicializa o banco de dados"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                servico TEXT NOT NULL,
                data DATE NOT NULL,
                horario TIME NOT NULL,
                dia_semana INTEGER NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()


def gerar_horarios(dia_semana):
    """
    Gera horários disponíveis baseado no dia da semana
    Seg-Sex: 18:30 até 21:00 (45 min de espaço)
    Sábado: 09:00 até 21:00 (45 min de espaço)
    """
    horarios = []
    
    if dia_semana == 6:  # Sábado
        inicio = datetime.strptime('09:00', '%H:%M')
        fim = datetime.strptime('21:00', '%H:%M')
    elif dia_semana in [1, 2, 3, 4, 5]:  # Seg-Sex
        inicio = datetime.strptime('18:30', '%H:%M')
        fim = datetime.strptime('21:00', '%H:%M')
    else:
        return horarios
    
    horario_atual = inicio
    while horario_atual <= fim:
        horarios.append(horario_atual.strftime('%H:%M'))
        horario_atual += timedelta(minutes=45)
    
    return horarios


def horarios_disponiveis(data, dia_semana):
    """Retorna apenas horários não agendados para a data especificada"""
    todos_horarios = gerar_horarios(dia_semana)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT horario FROM agendamentos WHERE data = ?', (data,))
    agendados = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return [h for h in todos_horarios if h not in agendados]


@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')


@app.route('/agendar', methods=['POST'])
def agendar():
    """Página de agendamento"""
    dia = request.form.get('dia')
    data = request.form.get('data')
    
    # Converte o número do dia para o nome
    nome_dia = DIAS_SEMANA.get(int(dia)) if dia else None
    
    # Obtém horários disponíveis para essa data
    dia_semana = int(dia) if dia else 0
    horarios = horarios_disponiveis(data, dia_semana)
    
    return render_template('agendar.html', 
                          nome_dia=nome_dia, 
                          data=data, 
                          dia=dia,
                          horarios=horarios)


@app.route('/confirmar', methods=['POST'])
def confirmar():
    """Página de confirmação"""
    nome = request.form.get('nome')
    dia = request.form.get('dia')
    data = request.form.get('data')
    horario = request.form.get('horario')
    servico = request.form.get('servico')
    telefone = request.form.get('telefone')
    
    # Salva no banco de dados
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (nome, telefone, servico, data, horario, dia_semana)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, telefone, servico, data, horario, int(dia)))
    conn.commit()
    conn.close()
    
    # Converte o número do dia para o nome
    nome_dia = DIAS_SEMANA.get(int(dia)) if dia else None
    
    return render_template('confirmar.html',
                          nome=nome,
                          dia=nome_dia,
                          data=data,
                          horario=horario,
                          servico=servico)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)
