import pandas as pd
import numpy as np
import locale
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import io
import bar_chart_race as bcr
import base64

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
pd.set_option("styler.render.max_elements", 300000)
dataset_file = './data/500+.csv'
css_file = './resources/style.css'
logo_file = './resources/logo.png''
icon_file = './resources/favicon.ico'

class InfoEdicao:

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

    def get_top_genero(self):
        top_genero = (self.df.groupby('Genero')
                       .size()
                       .reset_index(name='Count')
                       .sort_values(by='Count', ascending=False))
        top_genero = (top_genero[top_genero['Count'] == top_genero
                                   .drop_duplicates(subset='Count')
                                   .head(1)['Count']
                                   .values[0]])
        top_genero['Str'] = top_genero.Genero + ' (' + top_genero.Count.astype(str) + ')'
        return ', '.join(top_genero.Str)

    def get_repetidas(self):
        df_repetidas = self.df[self.df['Observacao'] == 'repetida'].groupby('Observacao').size().reset_index(name='Count')
        if df_repetidas.empty:
            return 'Não'
        else:
            return 'Sim (' + str(df_repetidas.Count.values[0]) + ')'

    def get_lista_paises(self):
        return self.df.groupby(['Edicao', 'Pais']).size().reset_index(name='Quantidade')

    def get_lista_generos(self):
        return self.df.groupby(['Edicao', 'Genero']).size().reset_index(name='Quantidade')

class InfoMusica:

    def __init__(self, df_data, id_musica):
        musica = df_data[df_data['Id'] == id_musica].Musica
        artista = df_data[df_data['Id'] == id_musica].Artista

        self.df = df_data.loc[(df_data['Artista'] == artista.values[0]) & (df_data['Musica'] == musica.values[0])]

    def get_melhor_posicao(self):
        return np.min(self.df.Posicao)

    def get_pior_posicao(self):
        return np.max(self.df.Posicao)

    def get_numero_aparicoes(self):
        return np.size(self.df.Posicao)

    def get_decada(self):
        return self.df.Decada_Lancamento_Album.values[0]

    def get_posicao_media(self):
        return np.mean(self.df.Posicao).round(0).astype(int)

class InfoCuriosidade:
    
    def __init__(self, df_data):
        self.df = df_data
        
    def __agrupar_dataframe(self, agregador):
        return self.df.groupby(agregador).size().reset_index(name = 'Count')
    
    def get_primeiro_artista_br(self):
        df = self.df[self.df['Pais'] == 'Brasil'].sort_values(['Ano', 'Posicao'], ascending=False).tail(1)
        return [df.Artista.values[0], df.Ano.values[0], df.Posicao.values[0]]
    
    def get_edicao_menos_artistas(self):
        df = self.__agrupar_dataframe(['Edicao', 'Artista']).groupby('Edicao')['Count'].count().reset_index().sort_values('Count')
        return [df.head(1).Edicao.values[0], df.head(1).Count.values[0]]
    
    def get_edicao_mais_artistas(self):
        df = self.__agrupar_dataframe(['Edicao', 'Artista']).groupby('Edicao')['Count'].count().reset_index().sort_values('Count')
        return [df.tail(1).Edicao.values[0], df.tail(1).Count.values[0]]
    
    def get_album_mais_musicas(self):
        df = self.__agrupar_dataframe(['Album_Single', 'Artista']).sort_values('Count').tail(1)
        return [df.Artista.values[0], df.Album_Single.values[0], df.Count.values[0], np.round(df.Count.values[0]/len(self.df)*100,2)]
    
    def get_artista_mais_musicas_edicao(self):
        df = self.__agrupar_dataframe(['Edicao', 'Artista']).sort_values('Count').tail(1)
        return [df.Artista.values[0], df.Count.values[0], df.Edicao.values[0]]
    
    def get_album_mais_musicas_edicao(self):
        df = self.__agrupar_dataframe(['Edicao', 'Album_Single']).sort_values('Count').sort_values('Count').tail(1)
        return [df.Album_Single.values[0], df.Count.values[0], df.Edicao.values[0]]
    
    def get_artista_maior_percentual(self):
        df = self.__agrupar_dataframe(['Artista']).sort_values('Count').tail(1)
        return [df.Artista.values[0], df.Count.values[0], np.round(df.Count.values[0]/len(self.df)*100,2)]

#Inicialização
@st.cache_data
def load_data(dataset, agregar_pinkfloyd):
    df_data = pd.read_csv(dataset)
    df_data['Id'] = range(1, len(df_data) + 1)
    df_data['Edicao'] = df_data.Ano.astype(str).str[-2:] + "-" + (df_data.Ano +1).astype(str).str[-2:]
    df_data['Data_Lancamento_Album'] = pd.to_datetime(df_data['Data_Lancamento_Album'])
    df_data['Decada_Lancamento_Album'] = df_data['Data_Lancamento_Album'].dt.year.apply(get_decada)

    if (agregar_pinkfloyd):
        df_data.loc[df_data['Musica'].str.contains('Another Brick', na=False), 'Musica'] = 'Another Brick in the Wall'

    return df_data

#Funções
def get_decada(ano):
    return 'Anos ' + str(ano)[2] + '0'

def filtrar_edicao(df_data, edicao_inicial, edicao_final):
    edicoes = np.unique(df_data.Edicao).tolist()
    indice_inicial = edicoes.index(edicao_inicial)
    indice_final = edicoes.index(edicao_final)+1
    edicoes_selecionadas = edicoes[indice_inicial:indice_final]
    return df_data[df_data['Edicao'].isin(edicoes_selecionadas)]

def filtrar_posicoes(df_data, posicao_inicial, posicao_final):
    posicoes = list(range(posicao_inicial, posicao_final + 1))
    return df_data[df_data['Posicao'].isin(posicoes)]

def filtrar_anos(df_data, ano_inicial, ano_final):
    anos = list(range(int(ano_inicial), int(ano_final) + 1))
    return df_data[df_data['Data_Lancamento_Album'].dt.year.isin(anos)]

def filtrar_inconsistencias(df_data):
    return df_data.loc[(df_data['Artista'] != '???') & (df_data['Musica'].str.len() > 0) & (df_data['Observacao'] != 'repetida')]

def get_primeiro_ano(df_data):
    return df_data.sort_values(by='Ano').head(1)['Ano']

def get_ultimo_ano(df_data):
    return df_data.sort_values(by='Ano').tail(1)['Ano']

def get_primeira_edicao(df_data):
    return df_data.sort_values(by='Ano').head(1)['Edicao']

def get_ultima_edicao(df_data):
    return df_data.sort_values(by='Ano').tail(1)['Edicao']

def get_primeiro_ano_lancamento(df_data):
    return df_listagem.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').head(1)['Data_Lancamento_Album'].dt.year

def get_ultimo_ano_lancamento(df_data):
    return df_listagem.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').tail(1)['Data_Lancamento_Album'].dt.year

def get_total_musicas_distintas(df_data):
    return len(get_musicas_distintas(df_data))

def get_total_generos_distintos(df_data):
    return len(get_generos_distintos(df_data))

def get_musicas_distintas(df_data):
    return filtrar_inconsistencias(df_data).drop_duplicates(subset=['Artista', 'Musica', 'Observacao'])

def get_generos_distintos(df_data):
    return filtrar_inconsistencias(df_data).drop_duplicates(subset='Genero')

@st.cache_data
def get_dicionario_musicas(df_data):
    df = (filtrar_inconsistencias(df_data)
                .drop_duplicates(subset={'Artista', 'Musica'})
                .apply(lambda row: (row['Musica'] + ' (' + row['Artista'] + ')', row['Id']), axis=1)
                .sort_values()
                .tolist())

    return dict((y, x) for x, y in df)

def get_acumulado_musicas_distintas(df_data):
    edicoes = np.unique(df_data.Edicao).tolist()
    distinta_acumulado_periodo = []
    for e in edicoes:
        distinta_acumulado_periodo.append(get_total_musicas_distintas(filtrar_edicao(df_data, edicoes[0], e)))
    return pd.DataFrame({'Anos': edicoes, 'Acumulado': distinta_acumulado_periodo})

def get_acumulado_generos_distintos(df_data):
    edicoes = np.unique(df_data.Edicao).tolist()
    distinto_acumulado_periodo = []
    for e in edicoes:
        distinto_acumulado_periodo.append(get_total_generos_distintos(filtrar_edicao(df_data, edicoes[0], e)))
    return pd.DataFrame({'Anos': edicoes, 'Acumulado': distinto_acumulado_periodo})

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

    return pd.pivot(data=df, index='Musica', columns='Edicao', values='Posicao')

def get_musicas_por_pais(df_data, agrupar_edicoes=False):
    df = filtrar_inconsistencias(df_data)
    if (agrupar_edicoes):
        return df.groupby(['Country', 'Pais']).size().reset_index(name='Total_Musicas')
    else:
        return (df.groupby(['Edicao', 'Pais'])
                  .size()
                  .reset_index(name='Total_Musicas')
                  .groupby(['Edicao', 'Pais'])
                  .agg({'Total_Musicas': 'sum'})
                  .reset_index()
                  .sort_values(by='Edicao')
                  .sort_values(by='Total_Musicas', ascending=True))

def get_musicas_por_genero(df_data):
    df = filtrar_inconsistencias(df_data)
    return (df.groupby(['Edicao', 'Genero'])
              .size()
              .reset_index(name='Total_Musicas')
              .groupby(['Edicao', 'Genero'])
              .agg({'Total_Musicas': 'sum'})
              .reset_index()
              .sort_values(by='Edicao')
              .sort_values(by='Total_Musicas', ascending=True))

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

def get_albuns_top_n(df_data, top_n):
    df = filtrar_posicoes(df_data, 1, top_n)
    df = (filtrar_inconsistencias(df)
          .groupby(['Artista', 'Album_Single'])
          .size()
          .sort_values(ascending=False)
          .reset_index(name='Total_Aparicoes'))
    return df

def get_generos_top_n(df_data, top_n):
    df = filtrar_posicoes(df_data, 1, top_n)
    df = (filtrar_inconsistencias(df)
          .groupby('Genero')
          .size()
          .sort_values(ascending=False)
          .reset_index(name='Total_Aparicoes'))
    return df

def get_top_n_musicas_media_posicao(df_data, top_n):
    df = get_musicas_media_posicao(df_data).loc[:,['Artista', 'Musica']]
    df['Posicao'] = range(1, len(df) + 1)
    return df[['Posicao', 'Artista', 'Musica']].head(top_n).set_index('Posicao')

def get_top_n_todas_edicoes(df_data, top_n):
    edicoes = np.unique(df_listagem.Edicao)
    edicao_inicial = edicoes[0]
    edicao_anterior = edicoes[len(edicoes) -2]
    df1 = get_top_n_musicas_media_posicao(df_data, top_n).reset_index()
    df2 = get_top_n_musicas_media_posicao(filtrar_edicao(df_data, edicao_inicial, edicao_anterior), 100).reset_index()

    merged_df = pd.merge(df1, df2, how='left', on = ['Artista', 'Musica'], suffixes=('_Atual', '_Anterior'))
    merged_df['Variacao'] = merged_df['Posicao_Anterior'] - merged_df['Posicao_Atual']

    return merged_df

def get_analise_periodo(df_data, medida, agregador):
    df =  filtrar_inconsistencias(df_data)
    df = df.groupby(agregador)['Musica'].count().reset_index(name='Contagem')
    match medida:
        case 'Média':
            df = df.groupby('Edicao')['Contagem'].mean().reset_index(name=medida)
        case 'Mediana':
            df = df.groupby('Edicao')['Contagem'].median().reset_index(name=medida)
        case 'Máximo':
            df = df.groupby('Edicao')['Contagem'].max().reset_index(name=medida)
        case default:
            df = df

    return np.around(df,2)

def get_idade_por_edicao(df_data):
    df = df_data.copy()
    df = filtrar_inconsistencias(df)
    df['Idade_Lancamento'] = df['Ano'] + 1 - df['Data_Lancamento_Album'].dt.year

    df = df.loc[:,['Edicao', 'Idade_Lancamento']]
    df['Media_Idade_Lancamento'] = df.groupby('Edicao')['Idade_Lancamento'].transform('mean').round(2)
    df['Mediana_Idade_Lancamento'] = df.groupby('Edicao')['Idade_Lancamento'].transform('median').round(0)

    return df.groupby(['Edicao', 'Media_Idade_Lancamento', 'Mediana_Idade_Lancamento']).size().reset_index()

def plotar_grafico_linha(df_data, xdata, ydata1, xlabel, ylabel1, ydata2 = None, ylabel2 = None):
    fig = px.line()
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel1, separators=',.')
    fig.add_scatter(x=df_data[xdata], y=df_data[ydata1], name=ylabel1)
    if (ydata2 != None):
        fig.add_scatter(x=df_data[xdata], y=df_data[ydata2], name=ylabel2)
    fig.update_traces(hovertemplate=xlabel + ': %{x}<br> Valor: %{y}<extra></extra>')

    st.plotly_chart(fig, use_container_width=True)

def plotar_grafico_barra(df_data, xdata, ydata, xlabel, ylabel, x_diagonal=False):
    fig = px.bar(df_data, x=xdata, y=ydata, text_auto=True)
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, separators=',.')
    fig.update_traces(marker_color='#C50B11', hovertemplate=xlabel + ": %{x}<br>" + ylabel + ": %{y}", textangle=0)
    if x_diagonal:
        fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def plotar_grafico_barra_horizontal(df_data, xdata, ydata, xlabel, ylabel, x_diagonal=False):
    df = df_data.sort_values(xdata, ascending = True)

    fig = go.Figure(go.Bar(
        x = df[xdata],
        y = df[ydata],
        hoverinfo = 'all',
        name='',
        textposition = 'outside',
        texttemplate='%{x}',
        hovertemplate = xlabel + ": %{x}<br>" + ylabel + ": %{y}",
        orientation = 'h',
        marker=dict(color='#C50B11'))
    )

    st.plotly_chart(fig, use_container_width=True)

def plotar_grafico_barra_stacked(df_data, xdata, ydata, ldata, xlabel, ylabel, llabel):
    fig = px.bar(df_data, x=xdata, y=ydata, color=ldata, color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, legend_title=llabel, legend_traceorder="reversed")
    fig.update_traces(hovertemplate='%{fullData.name}<br>' + xlabel + ": %{label}<br>" + ylabel + ": %{value}<extra></extra>")
    fig.update_xaxes(categoryorder='array', categoryarray=df_data.sort_values(xdata)[xdata].to_list())
    st.plotly_chart(fig, use_container_width=True)

def plotar_grafico_pizza(df_data, valor, nomes, label_valor, label_nomes):
    fig = px.pie(df_data, values=valor, names=nomes)
    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate=label_nomes + ": %{label}<br>" + label_valor + ": %{value}<br>" + 'Percentual' + ": %{percent}<br>")
    fig.update_layout(
        separators=',.',
        uniformtext_minsize=12, uniformtext_mode='hide',
        legend=dict(font=dict(size=14)),
        margin=dict(
            l=0,
            r=0,
            b=20,
            t=50,
            pad=0
        ))
    st.plotly_chart(fig, use_container_width=True)

def plotar_mapa(df_data):
    fig = px.choropleth(df_data, locationmode="country names", locations="Country", color='Total_Musicas', hover_name="Pais", color_continuous_scale=px.colors.sequential.YlOrRd, projection='natural earth')
    fig.update_layout(coloraxis_colorbar=dict(title="Quantidade de Músicas"))
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
                        hovertemplate='Edição: %{x}<br>Música: %{y}<br>Posição: %{z}',
                        texttemplate="%{text}"))

    fig.update_layout(xaxis_type='category',
                  xaxis_title = "Edições",
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

def plotar_treemap(df_data, xdata, ydata, xlabel, ylabel):
    fig = px.treemap(df_data, path=[px.Constant('Todos'), xdata], values=ydata, color=xdata, hover_data=[xdata])
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.update_traces(hovertemplate=xlabel + ": %{label}<br>" + ylabel + ": %{value}")
    st.plotly_chart(fig, use_container_width=True)

@st.cache_resource(show_spinner='Gerando gráfico de corrida...')
def gerar_grafico_race(df_data, atributo, titulo):
    df_data = filtrar_inconsistencias(df_data)
    df_data = (df_data.groupby(['Ano', atributo])
                  .size()
                  .reset_index(name='Count')
                  .groupby(['Ano', atributo])['Count']
                  .sum()
                  .groupby(level=atributo)
                  .cumsum()
                  .reset_index())
    df_data = df_data.sort_values(by='Count', ascending=False).groupby('Ano').head(len(df_data))
    df_values, df_ranks = bcr.prepare_long_data(df_data, index='Ano', columns=atributo, values='Count', steps_per_period=1)
    return bcr.bar_chart_race(df_values, n_bars=10, steps_per_period=15, period_length=1000, title = titulo, period_template='{x:.0f}', fixed_max=True, filter_column_colors=True).data

def plotar_grafico_race(html_data):
    start = html_data.find('base64,') + len('base64,')
    end = html_data.find('">')

    video = base64.b64decode(html_data[start:end])
    st.video(video)

def get_componente_top10(df_data):
    html = load_css()
    html+="""

      <div class="list">
          <div class="list__body">
            <table class="list__table">
              <tbody>
    """

    for index, row in df_data.iterrows():
        html += '<tr class="list__row"><td class="list__cell"><span class="list__value">' + str(row.Posicao_Atual) +'</span></td>'
        html += '<td class="list__cell"><span class="list__value">'+row.Musica+'</span><small class="list__label"></small></td>'
        html += '<td class="list__cell"><span class="list__value">'+row.Artista+'</span><small class="list__label"></small>'
        if (row.Variacao > 0):
            html += '</td><td class="list__cell list__icon__green">▲ ' + str(row.Variacao) + '</td></tr>'
        elif (row.Variacao < 0):
            html += '</td><td class="list__cell list__icon__red">▼ ' + str(row.Variacao * -1) + '</td></tr>'
        else:
            html += '</td><td class="list__cell list__icon__grey">■ 0</td></tr>'

    html+="""
            </tbody></table>
          </div>
        </div>

    """
    return components.html(html, height=600)

@st.cache_data
def load_css():
    with open(css_file) as f:
        return f'<style>{f.read()}</style>'

@st.cache_data
def show_data(df_data):
    st.dataframe(data=df_data.reset_index(drop=True).style.format(thousands=None), hide_index=True)

#App
st.set_page_config(layout="wide", 
                    page_title='As 500+ da Kiss',
                    page_icon=icon_file, 
                    menu_items={
                        'Get Help': 'https://github.com/denisvirissimo/500mais-kissfm',
                        'Report a bug': "https://github.com/denisvirissimo/500mais-kissfm/issues",
                        'About': "Desenvolvido por [Denis Bruno Viríssimo](https://www.linkedin.com/in/denisbruno/)"
                    })

if 'opt_pink_floyd' not in st.session_state:
    st.session_state.opt_pink_floyd = False

df_listagem = load_data(dataset_file, st.session_state.opt_pink_floyd)

list_aspectos = {"Músicas por Artista":['Artista', 'Edicao'], "Álbuns por Artista":['Album_Single', 'Edicao'], "Músicas por Gênero":['Genero', 'Edicao']}
list_variaveis = {"Artista": 'Artista', "Música": 'Musica', "Álbum/Single": 'Album', "Gênero": 'Genero'}
medidas = ["Média", "Mediana", "Máximo"]


#Sidebar
st.sidebar.subheader('Filtros')
st.sidebar.text('')

#Filtro Edições
edicoes = np.array(np.unique(df_listagem.Edicao).tolist())
edicao_inicial, edicao_final = st.sidebar.select_slider('Filtrar por edições', edicoes, value = [get_primeira_edicao(df_listagem).values[0], get_ultima_edicao(df_listagem).values[0]])
df_listagem_filtrada = filtrar_edicao(df_listagem, edicao_inicial, edicao_final)

#Filtro Posições
posicoes = np.unique(df_listagem.Posicao).tolist()
posicao_inicial, posicao_final = st.sidebar.select_slider('Filtrar por posições', posicoes, value=[min(posicoes), max(posicoes)])
df_listagem_filtrada = filtrar_posicoes(df_listagem_filtrada, posicao_inicial, posicao_final)

#Filtro Ano Lançamento
anos = np.unique(df_listagem.Data_Lancamento_Album.dropna().dt.year.apply(lambda x: f'{x:.0f}')).tolist()
ano_inicial, ano_final = st.sidebar.select_slider('Filtrar por anos de lançamento das músicas', anos, value=[min(anos), max(anos)])
df_listagem_filtrada = filtrar_anos(df_listagem_filtrada, ano_inicial, ano_final)

st.sidebar.caption('Estes filtros se aplicam somente às abas Visão Geral e Análises.')

st.sidebar.subheader('Opções')

st.sidebar.toggle('Agregar múltiplas versões de Another Brick in the Wall', key='opt_pink_floyd', help='[Clique aqui](https://github.com/denisvirissimo/500mais-kissfm#o-caso-de-another-brick-in-the-wall) para entender.')

col1, col2, col3 = st.columns((.2, 7.1, .2))

with col2:
    row1_1, row1_2 = st.columns((.25, 3.3), gap="small")
    with row1_1:
        st.image(logo_file, width=75)
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

    row2_1, row2_2, row2_3, row2_4, row2_5, row2_6 = st.columns((1.6, 1.6, 1.3, 1.6, 1.6, 1.6), gap="medium")
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
        str_total_artistas = "👨🏽‍🎤 " + locale.format_string("%d", total_artistas, grouping = True) + " artista(s)"
        st.markdown(str_total_artistas)
    with row2_4:
        total_albuns = len(np.unique(df_listagem_filtrada.Album_Single.dropna().astype(str)).tolist())
        str_total_albuns = "💿 " + locale.format_string("%d", total_albuns, grouping = True) + " álbum(s)/single(s)"
        st.markdown(str_total_albuns)
    with row2_5:
        total_paises = len(np.unique(df_listagem_filtrada.Pais.dropna()).tolist())
        str_total_paises = "🌎 " + locale.format_string("%d", total_paises, grouping = True) + " países representados"
        st.markdown(str_total_paises)
    with row2_6:
        total_generos = len(np.unique(df_listagem_filtrada.Genero.dropna()).tolist())
        str_total_generos = "🤘 " + locale.format_string("%d", total_generos, grouping = True) + " gêneros musicais"
        st.markdown(str_total_generos)

    st.divider()

    tab_geral, tab_edicao, tab_edicoes, tab_analises, tab_curiosidades = st.tabs(["Visão Geral", "Por Edição", "Todas as Edições", "Análises", "Curiosidades"])

    with tab_geral:
        st.subheader('Evolução de músicas distintas ao longo dos anos')
        plotar_grafico_barra(get_acumulado_musicas_distintas(df_listagem_filtrada), "Anos", "Acumulado", "Edições", "Acumulado de Músicas distintas")

        st.divider()

        st.subheader('Evolução de gêneros musicais distintos ao longo dos anos')
        plotar_grafico_barra(get_acumulado_generos_distintos(df_listagem_filtrada), "Anos", "Acumulado", "Edições", "Acumulado de Gêneros Musicais distintos")

        st.divider()

        st.subheader('Artistas, Músicas, Álbuns e Gêneros no Topo')

        row3_1, row3_2 = st.columns((2, 5), gap="large")
        with row3_1:
            top_n = st.slider('Qual Top N você deseja visualizar?', 1, 50, 3)
            variavel_topn_selecionada = st.selectbox ("Escolha a variável para visualizar no Top", list(list_variaveis.keys()), key = 'variavel_topn')
        with row3_2:
            match list_variaveis[variavel_topn_selecionada]:
                case 'Artista':
                    st.dataframe(data=get_artistas_top_n(df_listagem_filtrada, top_n), hide_index=True, use_container_width=True, height=400, column_config={"Artista":"Artista", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Musica':
                    st.dataframe(data=get_musicas_top_n(df_listagem_filtrada, top_n), hide_index=True, use_container_width=True, height=400, column_config={"Musica":"Música", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Album':
                    st.dataframe(data=get_albuns_top_n(df_listagem_filtrada, top_n), hide_index=True, use_container_width=True, height=400, column_config={"Album_Single":"Álbum/Single", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Genero':
                    st.dataframe(data=get_generos_top_n(df_listagem_filtrada, top_n), hide_index=True, use_container_width=True, height=400, column_config={"Genero":"Gênero", "Total_Aparicoes": "Número Total de Aparições"})
                case default:
                    st.write('Escolha uma opção')

        st.divider()

        st.subheader('Músicas distintas por Ano de Lançamento')
        plotar_grafico_barra(get_musicas_ano_lancamento(df_listagem_filtrada), "Data_Lancamento_Album", "Total_Musicas", "Anos", "Quantidade de Músicas distintas", True)

        st.divider()

        st.subheader('Músicas distintas por Década de Lançamento')
        plotar_grafico_barra(get_musicas_decada_lancamento(df_listagem_filtrada), "Decada_Lancamento_Album", "Total_Musicas", "Décadas", "Quantidade de Músicas distintas")

        st.divider()

        st.subheader('Músicas distintas por País do Artista')
        plotar_grafico_barra_stacked(get_musicas_por_pais(df_listagem_filtrada), "Edicao", "Total_Musicas", "Pais", "Edições", "Músicas por País", "Países")

        st.divider()

        st.subheader('Mapa de Países')
        plotar_mapa(get_musicas_por_pais(df_listagem_filtrada, True))

        st.divider()

        st.subheader('Músicas distintas por Gênero Musical do Artista')
        plotar_grafico_barra_stacked(get_musicas_por_genero(df_listagem_filtrada), "Edicao", "Total_Musicas", "Genero", "Edições", "Músicas por Gênero Musical", "Gêneros Musicais")

    with tab_edicao:

        st.markdown('Escolha uma edição e veja algumas informações relavantes:')

        row4_1, row4_2= st.columns((1.5, 6.2), gap="small")
        with row4_1:
            anos = np.array(np.unique(df_listagem.Ano).tolist())
            list_edicoes = dict(zip(edicoes, anos))
            edicao_selecionada = st.selectbox ("Edição", list_edicoes.keys(), key = 'edicao_selecionada')

        st.divider()

        row5_1, row5_2, row5_3 = st.columns((1.2, 2.6, 2.6), gap="large")

        with row5_1:
            st.subheader('Dados Gerais')
            info_edicao = InfoEdicao(df_listagem, list_edicoes[edicao_selecionada])

            st.markdown('Neste ano a 1ª posição ficou com **' + info_edicao.get_musica_posicao(1) + '** e a posição de número 500 com **' + info_edicao.get_musica_posicao(500) + '**.')

            st.markdown('O Artista em que mais apareceu na listagem foi **' + info_edicao.get_top_artista() + '**.')
            st.markdown('Já o Álbum/Single com mais músicas na lista foi **' + info_edicao.get_top_album() + '**.')

            st.markdown('O Gênero Musical mais tocado foi **' + info_edicao.get_top_genero() + '**.')

            st.markdown('E tivemos música repetida? **' + info_edicao.get_repetidas() + '**!')

        with row5_2:
            st.subheader('Países dos Artistas na Edição')
            plotar_grafico_pizza(info_edicao.get_lista_paises(), 'Quantidade', 'Pais', 'Músicas', 'País')

        with row5_3:
            st.subheader('Gêneros Musicais na Edição')
            plotar_grafico_pizza(info_edicao.get_lista_generos(), 'Quantidade', 'Genero', 'Músicas', 'Gênero Musical')

        st.subheader('Mapa de Gêneros Músicais')
        plotar_treemap(info_edicao.get_lista_generos(), 'Genero', 'Quantidade', 'Gênero', 'Quantidade de Músicas')

    with tab_analises:
        st.subheader('Análises por edição')
        st.markdown('A análise de alguns aspectos por edição pode mostrar a diversidade de músicas, álbuns e gêneros musicais a cada edição.')
        row7_1, row7_2 = st.columns((1.5, 6.2), gap="small")
        with row7_1:
            aspecto_edicao_selecionado = st.selectbox ("Escolha o aspecto", list(list_aspectos.keys()), key = 'aspecto_edicao')
            medida_edicao_selecionada = st.selectbox ("Escolha a medida", medidas, key = 'medida_edicao')
        with row7_2:
            plotar_grafico_barra(get_analise_periodo(df_listagem_filtrada, medida_edicao_selecionada, list_aspectos[aspecto_edicao_selecionado]),
                                "Edicao",
                                medida_edicao_selecionada,
                                "Edições",
                                medida_edicao_selecionada + ' de ' + aspecto_edicao_selecionado)

        st.divider()
        st.subheader('Idade das músicas')
        st.markdown('A análise de idade das músicas demonstra se há uma tradição de votação em músicas mais antigas (especialmente da década de 70) ou se têm sido incorporadas músicas mais recentes na listagem.')
        st.markdown('A idade é recalculada a cada edição.')

        plotar_grafico_linha(get_idade_por_edicao(df_listagem_filtrada), 'Edicao', 'Media_Idade_Lancamento', 'Edições', 'Média de Idade', 'Mediana_Idade_Lancamento', 'Mediana de Idade')

    with tab_curiosidades:

        info_curiosidades = InfoCuriosidade(filtrar_inconsistencias(df_listagem))

        curiosidade = info_curiosidades.get_primeiro_artista_br()
        st.markdown('* A primeira aparição de um artista brasileiro foi em {} com {}, ficando na {}ª posição.'.format(curiosidade[1], curiosidade[0], curiosidade[2]))

        curiosidade = info_curiosidades.get_edicao_menos_artistas()
        st.markdown('* A edição com menos artistas foi a {}, contando com "apenas" {} artistas.'.format(curiosidade[0], curiosidade[1]))

        curiosidade = info_curiosidades.get_edicao_mais_artistas()
        st.markdown('* Já a edição com mais artistas foi a {}, com {} artistas.'.format(curiosidade[0], curiosidade[1]))

        curiosidade = info_curiosidades.get_artista_mais_musicas_edicao()
        st.markdown('* O recorde de mais músicas em uma única edição é de {} com impressionantes {} músicas na edição {}.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

        curiosidade = info_curiosidades.get_album_mais_musicas_edicao()
        st.markdown('* O álbum/single com mais músicas em uma única edição é {} com {} músicas na edição {}.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

        curiosidade = info_curiosidades.get_album_mais_musicas()
        st.markdown('* O álbum/single com mais músicas em todas as edições é {} de {}, com {} músicas. Isto representa {} % de todas as músicas.'.format(curiosidade[1], curiosidade[0], curiosidade[2], curiosidade[3]))

        curiosidade = info_curiosidades.get_artista_maior_percentual()
        st.markdown('* {} é o artista com maior número de músicas: {}, o que representa {} % do total de músicas.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

    with tab_edicoes:

      row6_1, row6_2= st.columns((3.8, 3.8), gap="small")

      with row6_1:
          st.subheader('Top 10 de todas as edições')
          get_componente_top10(get_top_n_todas_edicoes(df_listagem, 10))
          st.caption('Para entender como essa lista foi criada, consulte [a explicação](https://github.com/denisvirissimo/500mais-kissfm#as-maiores-de-todos-os-tempos).')
      st.divider()

      st.subheader('Mapa de calor de músicas presentes em todas as edições')
      plotar_mapa_calor(get_musicas_todos_anos(df_listagem))

      st.divider()

      row7_1, row7_2= st.columns((3.5, 4.1), gap="small")
      with row7_1:
          st.subheader('Informações da música')

          lista_select = get_dicionario_musicas(df_listagem)
          musica_selecionada = st.selectbox(
              'Escolha a música',
              label_visibility='hidden',
              options=lista_select.keys(),
              index=None,
              placeholder='Digite ou escolha a música',
              format_func=lambda l: lista_select[l])

          st.text('')

      if (musica_selecionada != None):
          row8_1, row8_2, row8_3, row8_4, row8_5 = st.columns(5)
          info_musica = InfoMusica(filtrar_inconsistencias(df_listagem), musica_selecionada)
          row8_1.metric(label="Melhor Posição", value=info_musica.get_melhor_posicao())
          row8_2.metric(label="Pior Posição", value=info_musica.get_pior_posicao())
          row8_3.metric(label="Posição Média", value=info_musica.get_posicao_media())
          row8_4.metric(label="Aparições", value=info_musica.get_numero_aparicoes())
          row8_5.metric(label="Década", value=info_musica.get_decada())

      with row6_2:

          st.subheader('')
          plotar_grafico_race(gerar_grafico_race(
                              load_data(dataset_file, False),
                              'Artista',
                              'Top 10 Artistas com mais músicas nas edições'))

          plotar_grafico_race(gerar_grafico_race(
                              load_data(dataset_file, False),
                              'Genero',
                              'Top 10 Gêneros Musicais com mais músicas nas edições'))