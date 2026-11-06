"""Dashboard individual: alfabetização, escolaridade e deslocamento."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analise import carregar_arquivo, estatisticas, limpar_dados


st.set_page_config(page_title="Alfabetização e deslocamento | IBGE", layout="wide")
st.title("Alfabetização, escolaridade e deslocamento")
st.caption("Projeto Integrado · Aluno 2 · Censo Demográfico 2022 / IBGE")

st.sidebar.header("Dados e filtros")
upload = st.sidebar.file_uploader("Base tratada do IBGE (CSV ou XLSX)", type=["csv", "xlsx"])
local_data = Path(__file__).parent / "dados" / "alfabetizacao_ibge_2022.csv"
local_commute = Path(__file__).parent / "dados" / "deslocamento_ibge_2022.csv"
if upload is None and not local_data.exists():
    st.info("Envie a base tratada para iniciar a análise. O modelo de colunas está em dados/modelo_indicador.csv.")
    st.markdown("""**Fontes sugeridas:** [alfabetização, tabela SIDRA 9543](https://sidra.ibge.gov.br/tabela/9543) e [deslocamento para o trabalho, Censo 2022](https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html). A coluna de deslocamento é opcional; inclua-a somente quando os dados usarem a mesma unidade territorial e um período comparável.""")
    st.stop()

try:
    dados = limpar_dados(carregar_arquivo(upload) if upload else pd.read_csv(local_data))
except (ValueError, OSError, pd.errors.ParserError) as exc:
    st.error(f"Não foi possível carregar a base: {exc}")
    st.stop()
if dados.empty:
    st.warning("A base não contém registros válidos após a limpeza.")
    st.stop()

for col, label in (("ano", "Ano"), ("uf", "UF"), ("municipio", "Município"),
                   ("sexo", "Sexo"), ("cor_raca", "Cor ou raça"),
                   ("faixa_etaria", "Faixa etária"), ("nivel_instrucao", "Escolaridade")):
    if col in dados:
        opcoes = sorted(dados[col].dropna().unique().tolist())
        escolhidos = st.sidebar.multiselect(label, opcoes, default=opcoes)
        dados = dados[dados[col].isin(escolhidos)]

if dados.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

st.subheader("Taxa de alfabetização")
st.caption("Pessoas de 15 anos ou mais; valores em %. As estatísticas descrevem as linhas filtradas da base, sem ponderação populacional.")
stats = estatisticas(dados["taxa_alfabetizacao"])
cards = st.columns(4)
for card, name, key in zip(cards, ("Média", "Mediana", "IQR", "Desvio padrão"),
                           ("media", "mediana", "iqr", "desvio_padrao")):
    card.metric(name, f"{stats[key]:.2f} p.p.")

left, right = st.columns(2)
with left:
    por_uf = dados.groupby("uf", as_index=False)["taxa_alfabetizacao"].mean()
    fig = px.bar(por_uf, x="uf", y="taxa_alfabetizacao", labels={"uf": "UF", "taxa_alfabetizacao": "Taxa média das linhas (%)"}, title="Comparação territorial")
    st.plotly_chart(fig, use_container_width=True)
with right:
    distribuicao = dados.assign(grupo="UFs selecionadas")
    fig = px.box(
        distribuicao,
        x="grupo", y="taxa_alfabetizacao", points="all", hover_data=["uf"],
        labels={"grupo": "", "taxa_alfabetizacao": "Taxa de alfabetização (%)", "uf": "UF"},
        title="Distribuição das taxas entre UFs",
    )
    fig.update_traces(jitter=0.18, pointpos=-0.65, marker=dict(size=6, opacity=0.8))
    st.plotly_chart(fig, use_container_width=True)

st.write(f"**Quartis:** Q1 {stats['q1']:.2f}%, Q2 {stats['mediana']:.2f}%, Q3 {stats['q3']:.2f}%. "
         f"**Amplitude:** {stats['amplitude']:.2f} p.p. **Variância:** {stats['variancia']:.2f}. "
         f"**Outliers (1,5 × IQR):** {stats['outliers']} de {stats['n']} registros.")
if pd.notna(stats["moda"]):
    st.write(f"**Moda:** {stats['moda']:.2f}%.")
else:
    st.write("**Moda:** não há uma moda única nos valores filtrados.")
if stats["media"] > stats["mediana"]:
    st.write("A média está acima da mediana; valores altos podem elevá-la. Examine os pontos extremos antes de interpretar o valor típico.")
elif stats["media"] < stats["mediana"]:
    st.write("A média está abaixo da mediana; valores baixos podem reduzi-la. A mediana resiste melhor a extremos.")
else:
    st.write("Média e mediana coincidem nos registros filtrados.")

if upload is None and local_commute.exists():
    st.subheader("Escolaridade e tempo de deslocamento")
    st.caption("Censo 2022, tabela 10333: pessoas ocupadas de 10 anos ou mais que trabalhavam fora do domicílio. Tempo habitual de ida ao trabalho em faixas, sem estimar minutos individuais.")
    base = pd.read_csv(local_commute)
    base = base[base["uf"].isin(dados["uf"].unique())]
    base = base[base["nivel_id"] != 120704]
    totais = base[base["faixa_tempo_id"] == 31609].groupby("nivel_instrucao")["pessoas"].sum()
    longos = base[base["faixa_tempo_id"].isin([19432, 79191, 79192])].groupby("nivel_instrucao")["pessoas"].sum()
    tabela = (100 * longos.div(totais)).dropna().reset_index(name="percentual")
    grafico = px.bar(tabela, x="nivel_instrucao", y="percentual", text_auto=".1f",
                     labels={"nivel_instrucao": "Nível de instrução", "percentual": "Viagens acima de 1 hora (%)"},
                     title="Parcela com deslocamento acima de 1 hora")
    st.plotly_chart(grafico, use_container_width=True)
    st.caption("As proporções são calculadas com contagens de pessoas, somando as UFs selecionadas. Elas não revelam distância, causa da viagem nem a distribuição de minutos dentro de cada faixa.")

if "tempo_deslocamento_minutos" in dados and dados["tempo_deslocamento_minutos"].notna().any():
    st.subheader("Deslocamento ao trabalho")
    commute = dados.dropna(subset=["tempo_deslocamento_minutos"])
    travel = estatisticas(commute["tempo_deslocamento_minutos"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Tempo médio", f"{travel['media']:.1f} min")
    c2.metric("Tempo mediano", f"{travel['mediana']:.1f} min")
    c3.metric("Outliers", str(travel["outliers"]))
    chart = px.scatter(commute, x="taxa_alfabetizacao", y="tempo_deslocamento_minutos",
                       color="uf", hover_data=[col for col in ("municipio", "nivel_instrucao") if col in commute],
                       labels={"taxa_alfabetizacao": "Taxa de alfabetização (%)", "tempo_deslocamento_minutos": "Tempo de deslocamento (min)"},
                       title="Comparação entre indicadores territoriais")
    st.plotly_chart(chart, use_container_width=True)
    if "nivel_instrucao" in commute:
        chart = px.box(commute, x="nivel_instrucao", y="tempo_deslocamento_minutos", points="outliers",
                       labels={"nivel_instrucao": "Nível de instrução", "tempo_deslocamento_minutos": "Tempo de deslocamento (min)"},
                       title="Deslocamento por escolaridade")
        st.plotly_chart(chart, use_container_width=True)
    st.caption("Comparações territoriais não demonstram que a escolaridade causa o tempo de viagem. A base de alfabetização inclui pessoas de 15 anos ou mais; a de deslocamento cobre trabalhadores elegíveis conforme a tabela consultada. Verifique período, território e população antes de cruzar as fontes.")

with st.expander("Dados tratados e metodologia"):
    st.dataframe(dados, use_container_width=True)
    st.download_button("Baixar dados filtrados", dados.to_csv(index=False).encode("utf-8-sig"), "dados_filtrados.csv", "text/csv")
    st.write("Desvio padrão e variância amostrais (ddof=1); quartis pelo método linear do Pandas; outlier abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR. Cada linha tem o mesmo peso nas estatísticas.")

st.subheader("Contexto para a roda de conversa")
st.image(str(Path(__file__).parent / "assets" / "educacao_mobilidade.svg"), caption="Ilustração autoral: educação e mobilidade")
st.markdown("""- [IBGE Educa: o que o Censo 2022 revela sobre alfabetização](https://educa.ibge.gov.br/jovens/materias-especiais/22316-o-que-o-censo-2022-tem-a-dizer-sobre-alfabetizacao.html)
- [IBGE: Censo 2022, deslocamento para trabalho e estudo](https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html)

**Pergunta para os gestores:** em quais territórios a baixa alfabetização e as viagens longas aparecem juntas, e que informações adicionais seriam necessárias para definir uma política pública?""")
