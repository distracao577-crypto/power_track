# 🚀 Power Track - Gestão Financeira com IA

O **Power Track** é uma aplicação Full Stack de controle financeiro pessoal que utiliza Inteligência Artificial para analisar seus gastos e fornecer insights em tempo real.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python com FastAPI (API REST)
- **Frontend:** Python com NiceGUI (Interface Web / Tailwind CSS)
- **Banco de Dados:** PostgreSQL 15
- **IA:** Groq API (Modelo Llama-3) para análise de dados via Streaming
- **Infraestrutura:** Docker & Docker Compose

## 📋 Funcionalidades

- ✅ **Dashboard Reativo:** Visualização de Saldo, Entradas e Saídas com atualização instantânea.
- ✅ **Filtros Inteligentes:** Consulta de transações por Mês e Ano (Task 2.2).
- ✅ **Gráfico de Gastos:** Visualização diária de despesas no mês atual.
- ✅ **Assistente de IA:** Chat integrado que "lê" seu extrato e responde dúvidas financeiras.
- ✅ **Persistência Segura:** Dados armazenados em banco de dados relacional.

## 🚀 Como Rodar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o **Docker** e o **Docker Compose** instalados na sua máquina (ou VM Ubuntu).

### 2. Configuração das Variáveis de Ambiente
Crie um arquivo chamado `.env` na raiz do projeto e adicione suas credenciais:

```env
DATABASE_URL=postgresql://user_power:senha_forte@db:5432/powertrack_db
GROQ_API_KEY=SUA_CHAVE_GROQ_AQUI
