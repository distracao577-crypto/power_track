from nicegui import ui
from datetime import date
import api_client
import httpx

# Variáveis globais para o formulário
desc = None
valor = None
tipo = None
dt = None
categoria = None

# Função que renderiza os cards e pode ser "recarregada" com novos dados
@ui.refreshable
async def renderizar_cards(mes=None, ano=None):
    try:
        dados = await api_client.get_dashboard(mes=mes, ano=ano)
    except Exception:
        dados = {"saldo_total": 0, "total_entradas": 0, "total_saidas": 0}

    with ui.row().classes('w-full gap-4'):
        for label, key, color in [('Saldo', 'saldo_total', 'indigo'), 
                                  ('Entradas', 'total_entradas', 'emerald'), 
                                  ('Saídas', 'total_saidas', 'rose')]:
            val = dados.get(key, 0)
            with ui.card().classes(f'flex-1 p-4 shadow-sm border-t-4 border-{color}-500'):
                ui.label(label).classes('text-xs uppercase font-bold text-slate-500')
                ui.label(f"R$ {val:,.2f}").classes(f'text-2xl font-bold text-{color}-600')

async def salvar():
    global desc, valor, tipo, dt, categoria
    payload = {
        "valor": float(valor.value) if valor.value else 0.0,
        "descricao": desc.value,
        "tipo": str(tipo.value).lower(),
        "data": dt.value 
    }
    if await api_client.post_transacao(payload):
        ui.notify('Registrado com sucesso!', color='positive')
        # Após salvar, recarrega os cards com o total acumulado
        await renderizar_cards.refresh()
        desc.set_value('')
        valor.set_value(None)
    else:
        ui.notify('Erro ao salvar no banco de dados', color='negative')

@ui.page('/')
async def index():
    global desc, valor, tipo, dt, categoria

    ui.query('body').style('background-color: #f1f5f9;')

    # Sidebar
    with ui.left_drawer(value=True).classes('bg-slate-900 text-white p-6'):
        ui.label('FINANÇAS AI').classes('text-2xl font-black mb-8 text-indigo-400')
        ui.button('Dashboard', icon='dashboard').props('flat').classes('w-full justify-start')

    with ui.column().classes('w-full p-8 max-w-6xl mx-auto gap-8'):
        
        # --- SEÇÃO DE FILTROS (Task 2.2) ---
        with ui.row().classes('w-full items-center gap-4 bg-white p-4 rounded shadow-sm'):
            ui.label('Filtrar Período:').classes('font-bold text-slate-600')
            
            mes_sel = ui.select({
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }, value=date.today().month).classes('w-40')
            
            ano_sel = ui.number(value=date.today().year, format='%d').classes('w-24')
            
            ui.button('Filtrar', on_click=lambda: renderizar_cards.refresh(mes_sel.value, int(ano_sel.value)))\
                .props('unelevated color=indigo')
            
            ui.button('Limpar Filtro', on_click=lambda: renderizar_cards.refresh())\
                .props('flat color=slate-500')

        # Chamada inicial dos Cards
        await renderizar_cards()

        with ui.row().classes('w-full gap-8 items-start'):
            # Gráfico
            with ui.card().classes('flex-[2] p-4 shadow-sm'):
                ui.label('Gastos por Dia (Mês Atual)').classes('text-lg font-bold mb-4')
                grafico_dados = await api_client.get_grafico()
                ui.highchart({
                    'chart': {'type': 'column', 'height': 300},
                    'xAxis': {'categories': list(range(1, 32))},
                    'series': [{'name': 'Gastos', 'data': grafico_dados, 'color': '#6366f1'}],
                }).classes('w-full')

            # Formulário
            with ui.card().classes('flex-1 p-6 shadow-sm'):
                ui.label('Nova Transação').classes('text-lg font-bold mb-4')
                desc = ui.input('Descrição').classes('w-full')
                valor = ui.number('Valor (R$)', format='%.2f').classes('w-full')
                tipo = ui.select({'entrada': 'Entrada', 'saida': 'Saída'}, value='saida').classes('w-full')
                dt = ui.input('Data').classes('w-full')
                dt.set_value(date.today().isoformat())
                with dt:
                    with ui.menu() as menu:
                        ui.date().bind_value(dt).on('change', menu.close)
                
                ui.button('SALVAR', on_click=salvar).classes('w-full bg-indigo-600 text-white mt-4 py-3')

        # SEÇÃO DE IA
        with ui.card().classes('w-full p-6 shadow-sm mb-8'):
            ui.label('Assistente Financeiro AI').classes('text-lg font-bold mb-2')
            chat_container = ui.scroll_area().classes('w-full h-48 bg-slate-50 p-4 border rounded mb-4')
            
            with ui.row().classes('w-full items-center gap-2'):
                pergunta_input = ui.input(placeholder='Ex: Qual meu saldo?').classes('flex-1')
                
                async def enviar_mensagem():
                    txt = pergunta_input.value
                    if not txt: return
                    pergunta_input.set_value('')
                    with chat_container:
                        ui.label(f"Você: {txt}").classes('font-bold text-indigo-700 mt-2')
                        resp_label = ui.label('IA: ...').classes('text-slate-800 italic')
                    
                    conteudo_ia = ""
                    try:
                        async for chunk in api_client.chat_ia_stream(txt):
                            conteudo_ia += chunk
                            resp_label.set_text(f"IA: {conteudo_ia}")
                            chat_container.scroll_to(percent=1.0)
                    except Exception as e:
                        ui.notify(f'Erro na IA: {e}', color='negative')

                ui.button(icon='send', on_click=enviar_mensagem).props('round elevated color=indigo')
                
                def limpar_chat():
                    chat_container.clear()
                    ui.notify('Chat limpo')
                ui.button(icon='delete_sweep', on_click=limpar_chat).props('round flat color=slate-400')

ui.run(host='0.0.0.0', port=8080, title='Finanças AI')
