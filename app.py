from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import os
import re

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para flash messages

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
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(data, horario)
            )
        ''')
        conn.commit()
        conn.close()


def validar_telefone(telefone):
    """Valida formato do telefone: (XX) XXXXX-XXXX"""
    padrao = r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
    return re.match(padrao, telefone) is not None


def validar_nome(nome):
    """Valida se o nome tem pelo menos 3 caracteres"""
    return nome and len(nome.strip()) >= 3


def validar_data(data_str):
    """Valida se a data não é no passado e é válida"""
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        hoje = datetime.now().date()
        return data >= hoje
    except:
        return False


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
    try:
        dia = request.form.get('dia', '').strip()
        data = request.form.get('data', '').strip()
        
        # Validações
        if not dia or not data:
            flash('❌ Por favor, selecione dia e data!', 'error')
            return redirect('/')
        
        if not validar_data(data):
            flash('❌ Data inválida ou no passado!', 'error')
            return redirect('/')
        
        dia_semana = int(dia)
        
        # Valida se o dia selecionado corresponde à data
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        if data_obj.weekday() + 1 != dia_semana and not (dia_semana == 6 and data_obj.weekday() == 6):
            # Ajuste para domingo (0)
            if not (dia_semana == 0 and data_obj.weekday() == 6):
                flash('❌ Dia e data não correspondem!', 'error')
                return redirect('/')
        
        # Converte o número do dia para o nome
        nome_dia = DIAS_SEMANA.get(dia_semana)
        
        # Obtém horários disponíveis para essa data
        horarios = horarios_disponiveis(data, dia_semana)
        
        return render_template('agendar.html', 
                              nome_dia=nome_dia, 
                              data=data, 
                              dia=dia,
                              horarios=horarios)
    except Exception as e:
        flash(f'❌ Erro ao processar agendamento: {str(e)}', 'error')
        return redirect('/')


@app.route('/confirmar', methods=['POST'])
def confirmar():
    """Página de confirmação"""
    try:
        nome = request.form.get('nome', '').strip()
        dia = request.form.get('dia', '').strip()
        data = request.form.get('data', '').strip()
        horario = request.form.get('horario', '').strip()
        servico = request.form.get('servico', '').strip()
        telefone = request.form.get('telefone', '').strip()
        
        # Validações
        if not validar_nome(nome):
            flash('❌ Nome inválido (mínimo 3 caracteres)!', 'error')
            return redirect('/')
        
        if not validar_telefone(telefone):
            flash('❌ Telefone inválido! Formato: (XX) XXXXX-XXXX', 'error')
            return redirect('/')
        
        if not data or not validar_data(data):
            flash('❌ Data inválida!', 'error')
            return redirect('/')
        
        if not horario or not servico:
            flash('❌ Selecione horário e serviço!', 'error')
            return redirect('/')
        
        # Verifica se o horário ainda está disponível (proteção contra race condition)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO agendamentos (nome, telefone, servico, data, horario, dia_semana)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nome, telefone, servico, data, horario, int(dia)))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('❌ Este horário já foi reservado! Escolha outro.', 'error')
            return redirect('/')
        finally:
            conn.close()
        
        # Converte o número do dia para o nome
        nome_dia = DIAS_SEMANA.get(int(dia))
        
        return render_template('confirmar.html',
                              nome=nome,
                              dia=nome_dia,
                              data=data,
                              horario=horario,
                              servico=servico,
                              telefone=telefone)
    except Exception as e:
        flash(f'❌ Erro ao confirmar agendamento: {str(e)}', 'error')
        return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=5000)
