import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import locale
import streamlit as st

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Info:

    def __init__(self, df_data, ano):
        self.df = df_data[df_data['Ano'] == ano]

    def get_musica_posicao(self, posicao):
        df_filtrado = self.df[self.df['Posicao'] == posicao]
        return df_filtrado.Artista.values[0] + ' - ' + df_filtrado.Musica.values[0]

    def get_top_artista(self):
        top_artista = (self.df.groupby('Artista')
                       .size()
                       .reset_index(name='Count')
                       .sort_values(by='Count', ascending=False))
        top_artista = (top_artista[top_artista['Count'] == top_artista
                                   .drop_duplicates(subset='Count')
                                   .head(1)['Count']
                                   .values[0]])
        top_artista['Str'] = top_artista.Artista + ' (' + top_artista.Count.astype(str) + ')'
        return ', '.join(top_artista.Str)

    def get_top_album(self):
        top_album = (self.df.groupby(['Album_Single', 'Artista'])
                       .size()
                       .reset_index(name='Count')
                       .sort_values(by='Count', ascending=False))
        top_album = (top_album[top_album['Count'] == top_album
                                   .drop_duplicates(subset='Count')
                                   .head(1)['Count']
                                   .values[0]])
        top_album['Str'] = top_album.Artista + ' - ' + top_album.Album_Single + ' (' + top_album.Count.astype(str) + ')'
        return ', '.join(top_album.Str)

    def get_repetidas(self):
        df_repetidas = self.df[self.df['Observacao'] == 'repetida'].groupby('Observacao').size().reset_index(name='Count')
        if df_repetidas.empty:
            return 'Não'
        else:
            return 'Sim (' + str(df_repetidas.Count.values[0]) + ')'

#Inicialização
@st.cache_data
def load_data(dataset):
    df_data = pd.read_csv(dataset)
    df_data['Id'] = range(1, len(df_data) + 1)
    df_data['Ano_Periodo'] = df_data.Ano.astype(str).str[-2:] + "-" + (df_data.Ano +1).astype(str).str[-2:]
    df_data['Data_Lancamento_Album'] = pd.to_datetime(df_data['Data_Lancamento_Album'])
    df_data['Decada_Lancamento_Album'] = df_data['Data_Lancamento_Album'].dt.year.apply(get_decada)
    return df_data

#Funções
def get_decada(ano):
    return 'Anos ' + str(ano)[2] + '0'

def filtrar_periodo(df_data, periodo_inicial, periodo_final):
    periodos = np.unique(df_data.Ano_Periodo).tolist()
    indice_inicial = periodos.index(periodo_inicial)
    indice_final = periodos.index(periodo_final)+1
    periodos_selecionados = periodos[indice_inicial:indice_final]
    return df_data[df_data['Ano_Periodo'].isin(periodos_selecionados)]

def filtrar_posicoes(df_data, posicao_inicial, posicao_final):
    posicoes = list(range(posicao_inicial, posicao_final + 1))
    return df_data[df_data['Posicao'].isin(posicoes)]

def filtrar_inconsistencias(df_data):
    return df_data.loc[(df_data['Artista'] != '???') & (df_data['Musica'].str.len() > 0) & (df_data['Observacao'] != 'repetida')]

def get_primeiro_ano(df_data):
    return df_data.sort_values(by='Ano').head(1)['Ano']

def get_ultimo_ano(df_data):
    return df_data.sort_values(by='Ano').tail(1)['Ano']

def get_primeiro_ano_periodo(df_data):
    return df_data.sort_values(by='Ano').head(1)['Ano_Periodo']

def get_ultimo_ano_periodo(df_data):
    return df_data.sort_values(by='Ano').tail(1)['Ano_Periodo']

def get_primeiro_ano_lancamento(df_data):
    return df_listagem.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').head(1)['Data_Lancamento_Album'].dt.year

def get_ultimo_ano_lancamento(df_data):
    return df_listagem.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').tail(1)['Data_Lancamento_Album'].dt.year

def get_total_musicas_distintas(df_data):
    return len(get_musicas_distintas(df_data))

def get_musicas_distintas(df_data):
    return filtrar_inconsistencias(df_data).drop_duplicates(subset=['Artista', 'Musica', 'Observacao'])

def get_acumulado_musicas_distintas(df_data):
    periodos = np.unique(df_data.Ano_Periodo).tolist()
    distinta_acumulado_periodo = []
    for p in periodos:
        distinta_acumulado_periodo.append(get_total_musicas_distintas(filtrar_periodo(df_data, periodos[0], p)))
    return pd.DataFrame({'Anos': periodos, 'Acumulado': distinta_acumulado_periodo})

def get_musicas_ano_lancamento(df_data):
    df_temp = get_musicas_distintas(df_data)
    return pd.DataFrame(df_temp.groupby(df_temp['Data_Lancamento_Album'].dt.year).size().reset_index().rename(columns={0: 'Total_Musicas'}))

def get_musicas_decada_lancamento(df_data):
    df_temp = get_musicas_distintas(df_data)
    df_temp['Total_Musicas'] = df_temp.groupby('Decada_Lancamento_Album')['Decada_Lancamento_Album'].transform('count')
    return pd.DataFrame(df_temp.sort_values('Data_Lancamento_Album').groupby(['Decada_Lancamento_Album', 'Total_Musicas']).head(1))[['Decada_Lancamento_Album', 'Total_Musicas']]

def get_musicas_todos_anos(df_data):
    df = filtrar_inconsistencias(df_data).copy()
    df['Count'] = df.groupby(['Artista', 'Musica', 'Observacao'], dropna=False)['Musica'].transform('count')
    df['Musica'] = df.apply(lambda row: row['Artista'] + ' - ' + row['Musica'], axis=1)
    df = df.loc[df['Count'] == 24].sort_values(['Ano','Posicao'])

    return pd.pivot(data=df, index='Musica', columns='Ano_Periodo', values='Posicao')

def get_musicas_media_posicao(df_data):
    #Fórmula Si = wi * Ai + (1 - wi) * S, em que:
    #wi = mi/mi+m_avg, sendo mi número total de aparições da música e m_avg média de todas as aparições de músicas
    #Ai = média aritmética da posição da música
    #S = média aritmética da posição de todas as músicas
    #Si = média bayesiana da posição da música
    #https://arpitbhayani.me/blogs/bayesian-average/

    df_distintas = filtrar_inconsistencias(df_data.copy())

    #Workaround devido a problema de index com NaN no pivot_table. Necessário preencher o que está NaN com um valor dummy para poder fazer o grouping
    #https://github.com/pandas-dev/pandas/issues/3729
    df_distintas['Observacao'] = df_distintas['Observacao'].fillna('dummy')

    df_totalizador = (df_distintas
        .groupby(['Artista', 'Musica', 'Observacao'], dropna=False)
        .size()
        .reset_index(name='Total_Aparicoes'))

    m_avg = df_totalizador['Total_Aparicoes'].mean()

    pivot_table = (pd.pivot_table(df_distintas,
                                  index=['Artista', 'Musica', 'Observacao'],
                                  columns='Ano',
                                  values='Posicao',
                                  margins=True,
                                  margins_name = 'Media_Posicao'))

    S = pivot_table.loc[('Media_Posicao', '', ''), 'Media_Posicao']

    newdf = (df_distintas
             .groupby(['Artista', 'Musica', 'Observacao'], dropna=False)
             .size()
             .reset_index(name='Total_Aparicoes'))

    merged_df = pd.merge(df_totalizador, pivot_table, on = ['Artista', 'Musica', 'Observacao'])

    merged_df['Media_Bayesiana_Posicao'] = get_bayesian_average(merged_df['Total_Aparicoes'], m_avg, merged_df['Media_Posicao'], S)

    return merged_df.sort_values('Media_Bayesiana_Posicao')

def get_bayesian_average(m, m_avg, A, S):
    w = m/(m+m_avg)
    return w * A + (1-w) * S

def get_artistas_top_n(df_data, top_n):
    df = filtrar_posicoes(df_data, 1, top_n)
    df = (filtrar_inconsistencias(df)
          .groupby('Artista')
          .size()
          .sort_values(ascending=False)
          .reset_index(name='Total_Aparicoes'))
    return df

def get_musicas_top_n(df_data, top_n):
    df = filtrar_posicoes(df_data, 1, top_n)
    df = (filtrar_inconsistencias(df)
          .groupby(['Artista', 'Musica'])
          .size()
          .sort_values(ascending=False)
          .reset_index(name='Total_Aparicoes'))
    return df

def get_top_n_todas_edicoes(df_data, top_n):
    df = get_musicas_media_posicao(df_data).loc[:,['Artista', 'Musica']]
    df['Posicao'] = range(1, len(df) + 1)
    return df[['Posicao', 'Artista', 'Musica']].head(top_n).set_index('Posicao')

def get_analise_periodo(df_data, medida, agregador):
    df =  filtrar_inconsistencias(df_data)
    df = df.groupby(agregador)['Musica'].count().reset_index(name='Contagem')
    match medida:
        case 'Contagem':
            df = df.groupby('Ano_Periodo').sum().reset_index()
        case 'Média':
            df = df.groupby('Ano_Periodo')['Contagem'].mean().reset_index(name=medida)
        case 'Mediana':
            df = df.groupby('Ano_Periodo')['Contagem'].median().reset_index(name=medida)
        case 'Mínimo':
            df = df.groupby('Ano_Periodo')['Contagem'].min().reset_index(name=medida)
        case 'Máximo':
            df = df.groupby('Ano_Periodo')['Contagem'].max().reset_index(name=medida)
        case default:
            df = df

    return np.around(df,2)

def plotar_grafico_barra(df_data, xdata, ydata, xlabel, ylabel):
    fig = px.bar(df_data, x=xdata, y=ydata, text_auto=True)
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel)
    fig.update_traces(marker_color='#C50B11')
    st.plotly_chart(fig, use_container_width=True)

def plotar_mapa_calor(df_data):
    fig = go.Figure(data=go.Heatmap(
                        z=df_data,
                        x=df_data.columns,
                        y=df_data.index,
                        text=df_data,
                        colorscale='viridis',
                        reversescale=True,
                        name="",
                        hovertemplate='Ano: %{x}<br>Música: %{y}<br>Posição: %{z}',
                        texttemplate="%{text}"))

    fig.update_layout(xaxis_type='category',
                  xaxis_title = "Anos",
                  yaxis_title="Músicas",
                  height=55*len(df_data.index),
                  dragmode=False,
                  clickmode='none',
                  showlegend=False)

    fig.update_yaxes(tickvals=df_data.index, ticktext=[label + '  ' for label in df_data.index])
    fig['layout']['yaxis']['autorange'] = "reversed"


    config = {'scrollZoom': False,
          'modeBarButtonsToRemove': [
              'zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']}

    st.plotly_chart(fig, use_container_width=True, config = config)

@st.cache_data
def show_data(df_data):
    st.dataframe(data=df_data.reset_index(drop=True).style.format(thousands=None), hide_index=True)

#App
st.set_page_config(layout="wide")
df_listagem = load_data("./data/500+.csv")

list_aspectos = {"Músicas por Artista":['Artista', 'Ano_Periodo'],"Álbuns por Artista":['Album_Single', 'Ano_Periodo']}
medidas = ["Contagem", "Média", "Mediana", "Máximo", "Mínimo"]

#Sidebar
st.sidebar.text('Filtros')
st.sidebar.text('')

#Filtro Períodos
periodos = np.array(np.unique(df_listagem.Ano_Periodo).tolist())
periodo_inicial, periodo_final = st.sidebar.select_slider('Selecione os anos para filtrar as análises', periodos, value = [get_primeiro_ano_periodo(df_listagem).values[0], get_ultimo_ano_periodo(df_listagem).values[0]])
df_listagem_filtrada = filtrar_periodo(df_listagem, periodo_inicial, periodo_final)

#Filtro Posições
posicoes = np.unique(df_listagem.Posicao).tolist()
posicao_inicial, posicao_final = st.sidebar.select_slider('Selecione as posições das 500+ para filtrar as análises', posicoes, value=[min(posicoes), max(posicoes)])
df_listagem_filtrada = filtrar_posicoes(df_listagem_filtrada, posicao_inicial, posicao_final)


col1, col2, col3 = st.columns((.2, 7.1, .2))

with col2:
    row1_1, row1_2 = st.columns((.25, 3.3), gap="small")
    with row1_1:
        st.image('logo.jpg', width=75)
    with row1_2:
        st.title('As 500+ da Kiss FM')

    st.markdown("Esse é um projeto de Ciência de Dados com o objetivo de analisar a listagem das 500+ da rádio Kiss FM. A ideia surgiu a partir da curiosidade de saber qual seria a música número 1 de todas as votações até então, e acabou levando ao desenvolvimento de várias outras análises interessantes.")
    st.markdown("Todo o detalhamento do projeto, inclusive o tratamento de dados e algumas curiosidades, está disponível neste [repositório do GitHub](https://github.com/denisvirissimo/500mais-kissfm)")

    st.markdown("")
    with st.status("Carregando...") as status:
        show_data(df_listagem)
        status.update(label="Clique aqui para ver a listagem completa", state="complete")
    
    st.text('')
    st.subheader("Exibindo os seguintes dados a partir dos filtros:")

    row2_1, row2_2, row2_3, row2_4 = st.columns((1.6, 1.6, 1.6, 1.6), gap="medium")
    with row2_1:
        total_musicas = df_listagem_filtrada.Id.nunique()
        str_total_musicas = "🎶 " + locale.format_string("%d", total_musicas, grouping = True) + " músicas no total"
        st.markdown(str_total_musicas)
    with row2_2:
        total_musicas_distintas = get_total_musicas_distintas(df_listagem_filtrada)
        str_total_musicas_distintas = "🎵 " + locale.format_string("%d", total_musicas_distintas, grouping = True) + " músicas diferentes"
        st.markdown(str_total_musicas_distintas)
    with row2_3:
        total_artistas = len(np.unique(df_listagem_filtrada.Artista.dropna()).tolist())
        str_total_artistas = "🧑‍🎤 " + locale.format_string("%d", total_artistas, grouping = True) + " artista(s)"
        st.markdown(str_total_artistas)
    with row2_4:
        total_albuns = len(np.unique(df_listagem_filtrada.Album_Single.dropna().astype(str)).tolist())
        str_total_albuns = "💿 " + locale.format_string("%d", total_albuns, grouping = True) + " álbum(s)/single(s)"
        st.markdown(str_total_albuns)

    st.divider()

    st.subheader('Evolução de músicas distintas ao longo dos anos')
    plotar_grafico_barra(get_acumulado_musicas_distintas(df_listagem_filtrada), "Anos", "Acumulado", "Anos", "Acumulado de Músicas distintas")

    row3_1, row3_2 = st.columns((3.1, 3.1), gap="small")
    with row3_1:
        st.subheader('Artistas presentes no Top 3')
    with row3_2:
        st.subheader('Artistas presentes no Top 10')

    row4_1, row4_2 = st.columns((3.1, 3.1), gap="small")
    with row4_1:
        st.dataframe(data=get_artistas_top_n(df_listagem_filtrada, 3), hide_index=True, use_container_width=True, height=400, column_config={"Artista":"Artista", "Total_Aparicoes": "Número Total de Aparições"})
    with row4_2:
        st.dataframe(data=get_artistas_top_n(df_listagem_filtrada, 10), hide_index=True, use_container_width=True, height=400, column_config={"Artista":"Artista", "Total_Aparicoes": "Número Total de Aparições"})

    row5_1, row5_2 = st.columns((3.1, 3.1), gap="small")
    with row5_1:
        st.subheader('Músicas presentes no Top 3')
    with row5_2:
        st.subheader('Músicas presentes no Top 10')

    row6_1, row6_2 = st.columns((3.1, 3.1), gap="small")
    with row6_1:
        st.dataframe(data=get_musicas_top_n(df_listagem_filtrada, 3), hide_index=True, use_container_width=True, height=400, column_config={"Musica":"Música", "Total_Aparicoes": "Número Total de Aparições"})
    with row6_2:
        st.dataframe(data=get_musicas_top_n(df_listagem_filtrada, 10), hide_index=True, use_container_width=True, height=400, column_config={"Musica":"Música", "Total_Aparicoes": "Número Total de Aparições"})

    st.divider()

    st.subheader('Músicas distintas por Ano')
    plotar_grafico_barra(get_musicas_ano_lancamento(df_listagem_filtrada), "Data_Lancamento_Album", "Total_Musicas", "Anos", "Quantidade de Músicas distintas")

    st.divider()

    st.subheader('Músicas distintas por Década')
    plotar_grafico_barra(get_musicas_decada_lancamento(df_listagem_filtrada), "Decada_Lancamento_Album", "Total_Musicas", "Décadas", "Quantidade de Músicas distintas")

    st.divider()

    st.subheader('Mapa de calor de músicas presentes em todas as edições')
    plotar_mapa_calor(get_musicas_todos_anos(df_listagem))

    st.divider()

    st.subheader('Análises por edição')

    row7_1, row7_2 = st.columns((1.5, 6.2), gap="small")
    with row7_1:
        aspecto_edicao_selecionado = st.selectbox ("Escolha o aspecto", list(list_aspectos.keys()), key = 'aspecto_edicao')
        medida_edicao_selecionada = st.selectbox ("Escolha a medida", medidas, key = 'medida_edicao')
    with row7_2:
        plotar_grafico_barra(get_analise_periodo(df_listagem_filtrada, medida_edicao_selecionada, list_aspectos[aspecto_edicao_selecionado]),
                            "Ano_Periodo",
                            medida_edicao_selecionada,
                            "Anos",
                            medida_edicao_selecionada + ' de ' + aspecto_edicao_selecionado)

    st.divider()

    st.subheader('Top 10 de todas as edições')
    st.table(get_top_n_todas_edicoes(df_listagem, 10))

'''

info = Info(df_listagem, 2000)
info.get_musica_posicao(1)
info.get_musica_posicao(500)
info.get_top_artista()
info.get_repetidas()
info.get_top_album()

'''