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

def get_decada(ano):
    return 'Anos ' + str(ano)[2] + '0'

#Inicialização
df_listagem = pd.read_csv("./data/500+.csv")
df_listagem['Id'] = range(1, len(df_listagem) + 1)
df_listagem['Ano_Periodo'] = df_listagem.Ano.astype(str).str[-2:] + "-" + (df_listagem.Ano +1).astype(str).str[-2:]
df_listagem['Data_Lancamento_Album'] = pd.to_datetime(df_listagem['Data_Lancamento_Album'])
df_listagem['Decada_Lancamento_Album'] = df_listagem['Data_Lancamento_Album'].dt.year.apply(get_decada)

#Funções
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
          .groupby('Musica')
          .size()
          .sort_values(ascending=False)
          .reset_index(name='Total_Aparicoes'))
    return df

def get_analise_periodo(df_data, medida, agregador):
    df =  filtrar_inconsistencias(df_data)
    df = df.groupby(agregador)['Musica'].count().reset_index()
    match medida:
        case 'Contagem':
            return df.groupby('Ano_Periodo').sum().reset_index()
        case 'Média':
            return df.groupby('Ano_Periodo')['Musica'].mean().reset_index()
        case 'Mediana':
            return df.groupby('Ano_Periodo')['Musica'].median().reset_index()
        case 'Mínimo':
            return df.groupby('Ano_Periodo')['Musica'].min().reset_index()
        case 'Máximo':
            return df.groupby('Ano_Periodo')['Musica'].max().reset_index()
        case default:
            return df

def plotar_grafico_barra(df_data, xdata, ydata, xlabel, ylabel, decimal=False, rotacao=0):
    rc = {'figure.figsize':(12,4.5),
      'axes.facecolor':'#0e1117',
      'axes.edgecolor': '#0e1117',
      'axes.labelcolor': 'white',
      'figure.facecolor': '#0e1117',
      'patch.edgecolor': '#0e1117',
      'text.color': 'white',
      'xtick.color': 'white',
      'ytick.color': 'white',
      'grid.color': 'grey',
      'font.size' : 8,
      'axes.labelsize': 12,
      'xtick.labelsize': 8,
      'ytick.labelsize': 12}

    plt.rcParams.update(rc)
    fig, ax = plt.subplots()

    ax = sb.barplot(x=xdata, y=ydata, data=df_data, color = "#b80606")
    ax.set(xlabel = xlabel, ylabel = ylabel)
    plt.xticks(rotation=66,horizontalalignment="right")
    for p in ax.patches:
        if decimal:
            text = format(p.get_height(), '.2f')
        else:
            text = format(str(int(p.get_height())))
        ax.annotate(text,
              (p.get_x() + p.get_width() / 2., p.get_height()),
                ha = 'center',
                va = 'center',
                xytext = (0, 18),
                rotation = rotacao,
                textcoords = 'offset points')
    plt.show()

def plotar_mapa_calor(df_data):
    plt.figure(figsize=(20,9.5))
    plt.tick_params(axis='both', which='major', labelsize=10, labelbottom = True, bottom=True, top = True, labeltop=True)
    sb.heatmap(df_data, cmap='viridis_r', annot=True, cbar=False, fmt='g')
    plt.show()

#App
st.set_page_config(layout="wide")

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('As 500+ da Kiss FM')

row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown("Esse é um projeto de Ciência de Dados com o objetivo de analisar a listagem das 500+ da rádio Kiss FM. A ideia surgiu a partir da curiosidade de saber qual seria a música número 1 de todas as votações até então, e acabou levando ao desenvolvimento de várias outras análises interessantes.")
    st.markdown("Todo o detalhamento do projeto, inclusive o tratamento de dados e algumas curiosidades, está disponível neste [repositório do GitHub](https://github.com/denisvirissimo/500mais-kissfm)")

st.sidebar.text('Filtros')
st.sidebar.text('')
st.sidebar.text('')

#Filtro Períodos
st.sidebar.markdown("Selecione o período de anos")
periodos = np.array(np.unique(df_listagem.Ano_Periodo).tolist())
periodo_inicial, periodo_final = st.sidebar.select_slider('Selecione os anos para filtrar as análises', periodos, value = [get_primeiro_ano_periodo(df_listagem).values[0], get_ultimo_ano_periodo(df_listagem).values[0]])
df_listagem_filtrada = filtrar_periodo(df_listagem, periodo_inicial, periodo_final)

#Filtro Posições
posicoes = np.unique(df_listagem.Posicao).tolist()
posicao_inicial, posicao_final = st.sidebar.select_slider('Selecione as posições das 500+ para filtrar as análises', posicoes, value=[min(posicoes), max(posicoes)])
df_listagem_filtrada = filtrar_posicoes(df_listagem_filtrada, posicao_inicial, posicao_final)   

row3_spacer1, row3_1, row3_spacer2 = st.columns((.2, 7.1, .2))
with row3_1:
    st.markdown("")
    see_data = st.expander('Clique aqui para ver a listagem completa')
    with see_data:
        st.dataframe(data=df_listagem.reset_index(drop=True).style.format(thousands=None), hide_index=True)
st.text('')

'''
df_listagem_filtrada = filtrar_periodo(df_listagem, '00-01', '23-24')
df_listagem_filtrada = filtrar_posicoes(df_listagem_filtrada, 1, 500)

total_musicas = df_listagem_filtrada.Id.nunique()
total_musicas_distintas = get_total_musicas_distintas(df_listagem_filtrada)
total_artistas = len(np.unique(df_listagem_filtrada.Artista.dropna()).tolist())
total_albuns = len(np.unique(df_listagem_filtrada.Album_Single.dropna().astype(str)).tolist())

str_total_musicas = "🎶 " + locale.format_string("%d", total_musicas, grouping = True) + " músicas no total"
str_total_musicas_distintas = "🎵 " + locale.format_string("%d", total_musicas_distintas, grouping = True) + " músicas diferentes"
str_total_artistas = "🧑‍🎤 " + locale.format_string("%d", total_artistas, grouping = True) + " artista(s)"
str_total_albuns = "💿 " + locale.format_string("%d", total_albuns, grouping = True) + " álbum(s)/single(s)"

print(str_total_musicas, str_total_musicas_distintas, str_total_artistas, str_total_albuns, "\n")

get_musicas_media_posicao(df_listagem_filtrada)

get_artistas_top_n(df_listagem, 3)
get_artistas_top_n(df_listagem, 10)

get_musicas_top_n(df_listagem, 3)
get_musicas_top_n(df_listagem, 10)

info = Info(df_listagem, 2000)
info.get_musica_posicao(1)
info.get_musica_posicao(500)
info.get_top_artista()
info.get_repetidas()
info.get_top_album()

plotar_grafico_barra(get_acumulado_musicas_distintas(df_listagem_filtrada), "Anos", "Acumulado", "Anos", "Acumulado de Músicas distintas")

plotar_grafico_barra(get_musicas_ano_lancamento(df_listagem_filtrada), "Data_Lancamento_Album", "Total_Musicas", "Anos", "Quantidade de Músicas distintas")

plotar_grafico_barra(get_musicas_decada_lancamento(df_listagem_filtrada), "Decada_Lancamento_Album", "Total_Musicas", "Décadas", "Quantidade de Músicas distintas")

plotar_grafico_barra(get_analise_periodo(df_listagem_filtrada, "Média", ['Artista', 'Ano_Periodo']), "Ano_Periodo", "Musica", "Anos", "Músicas por Artista", True)

plotar_grafico_barra(get_analise_periodo(df_listagem_filtrada, 'Média', ['Album_Single', 'Ano_Periodo']), "Ano_Periodo", "Musica", "Anos", "Álbuns por Artista", True)

plotar_mapa_calor(get_musicas_todos_anos(df_listagem))
'''