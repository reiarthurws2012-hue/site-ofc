# 💈 Santana Barber - Sistema de Agendamentos

Um sistema web de agendamentos para barbearia desenvolvido com Flask, HTML, CSS e SQLite.

## 📋 Funcionalidades

✅ **Agendamento online** - Clientes podem agendar via web  
✅ **Horários automáticos** - Gerados conforme dias da semana:
- **Segunda a Sexta**: 18:30 às 21:00 (45 min de intervalo)
- **Sábado**: 09:00 às 21:00 (45 min de intervalo)

✅ **Horários filtrados** - Só mostra horários disponíveis  
✅ **Banco de dados** - Armazena agendamentos em SQLite  
✅ **Validações** - Nome, telefone, data, horário  
✅ **Proteção contra duplicatas** - Impede dois agendamentos no mesmo horário  
✅ **Design responsivo** - Funciona em celular, tablet e desktop  
✅ **Mensagens de erro** - Feedback visual para o usuário

## 🚀 Como Executar

### 1. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 📁 Estrutura do Projeto

```
barbearia/
├── app.py                          # Aplicação Flask principal
├── requirements.txt                # Dependências do projeto
├── agendamentos.db                 # Banco de dados SQLite (criado automaticamente)
├── static/
│   ├── style.css                   # Estilos CSS
│   └── WhatsApp Image 2026-06-19 at 15.18.56.jpeg  # Imagem da barbearia
└── templates/
    ├── index.html                  # Página inicial
    ├── agendar.html                # Página de agendamento
    └── confirmar.html              # Página de confirmação
```

## 🔐 Validações Implementadas

- ✅ **Nome**: Mínimo 3 caracteres
- ✅ **Telefone**: Formato (XX) XXXXX-XXXX (validado no cliente e servidor)
- ✅ **Data**: Não permite datas no passado
- ✅ **Horário**: Apenas horários disponíveis são exibidos
- ✅ **Serviço**: Opções fixas (Corte, Máquina, Barba, Corte + Barba)
- ✅ **Race condition**: Proteção contra dois usuários marcarem o mesmo horário

## 💻 Banco de Dados

Tabela `agendamentos`:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único (chave primária) |
| nome | TEXT | Nome do cliente |
| telefone | TEXT | Telefone de contato |
| servico | TEXT | Serviço contratado |
| data | DATE | Data do agendamento |
| horario | TIME | Horário do agendamento |
| dia_semana | INTEGER | Dia da semana (1-6, sem domingo) |
| data_criacao | TIMESTAMP | Data/hora de criação do agendamento |

**Constraint**: `UNIQUE(data, horario)` - Impede agendamentos duplicados

## 🎨 Estilos

- Tema profissional em ouro (#d4a574) e marrom
- Gradientes e sombras modernas
- Totalmente responsivo
- Interface intuitiva e fácil de usar

## 🔧 Melhorias Implementadas

### Segurança
- Validação no servidor (não depende só do cliente)
- Proteção contra SQL injection (uso de parâmetros)
- Transações de banco de dados contra race conditions
- Secret key para sessões Flask

### UX/UI
- Mensagens de erro claras e visuais
- Feedback em tempo real
- Horários sem disponibilidade mostram aviso
- Telefone com máscara de entrada
- Botões "Voltar" para fácil navegação

### Funcionalidade
- Agendamentos persistentes em banco de dados
- Sincronização entre dia selecionado e data
- Serviços com preços listados
- Formatos validados antes de salvar

## 📱 Responsividade

O site funciona perfeitamente em:
- 📱 Celulares (até 480px)
- 📱 Tablets (até 768px)
- 💻 Desktops (acima de 768px)

## 🚨 Notas Importantes

1. **Primeira execução**: O arquivo `agendamentos.db` é criado automaticamente
2. **Debug mode**: Ativado por padrão (`debug=True`)
3. **Horários**: Domingo não tem agendamentos
4. **Formato de telefone**: Obrigatório usar (XX) XXXXX-XXXX

## 📝 Exemplo de Uso

1. Acesse http://localhost:5000
2. Selecione dia da semana OU data
3. Clique em "Agendar"
4. Preencha nome, telefone, horário e serviço
5. Clique em "Confirmar horário"
6. Confirme os dados na página de sucesso

## 🐛 Troubleshooting

**Erro: "Port 5000 already in use"**
```bash
python app.py  # Tenta porta 5001, 5002, etc
```

**Erro: "Nenhum horário disponível"**
- Verifique se escolheu uma data válida
- Horários esgotam quando todos são agendados

**Banco de dados corrompido?**
- Delete `agendamentos.db`
- Reinicie a aplicação (banco será recriado)

## 📞 Contato

Para melhorias ou dúvidas, abra uma issue!

---

**Desenvolvido com ❤️ em Flask**
