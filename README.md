# 🚀 LLM Analytics Streamlit Dashboard

Este projeto é um dashboard interativo desenvolvido com [Streamlit](https://streamlit.io/) para visualização de métricas de latência de diferentes provedores de LLM (Large Language Models). Ele apresenta estatísticas, gráficos e filtros para análise detalhada dos dados de latência.

## Funcionalidades
- Filtro de período (data e hora) para análise personalizada
- Estatísticas gerais e por provedor (média, máxima, mínima, percentis)
- Boxplots de latência (geral e individual por provedor)
- Gráfico de barras de latência por requisição
- Visualização dos percentis por provedor
- Tabela detalhada dos dados

## Como executar
1. **Pré-requisitos:**
   - Python 3.8+
   - Fonte de dados configurada conforme sua necessidade

2. **Instale as dependências:**
   ```powershell
   pip install streamlit pandas numpy plotly python-dotenv
   ```

3. **Configure as variáveis de ambiente conforme sua fonte de dados.**

4. **Execute o dashboard:**
   ```powershell
   streamlit run metrics_dashboard.py
   ```

## Licença
Este projeto é distribuído sob a licença MIT.

---
<p align="center">UERJ 💙🧡</p>
