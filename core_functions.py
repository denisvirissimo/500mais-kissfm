import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import bar_chart_race as bcr
import io
import time
import json

#Configuração
pd.set_option("styler.render.max_elements", 350000)
dataset_file = './data/500+.csv'

class InfoEdicao:

    def __init__(self, df_data, ano):
        self.df = df_data[df_data['Ano'] == ano]

    def get_musica_posicao(self, posicao):
        df_filtrado = self.df[self.df['Posicao'] == posicao]
        return df_filtrado.Artista.values[0] + ' - ' + df_filtrado.Musica.values[0]

    def get_musica_menor_duracao(self):
        df_filtrado = self.df.dropna(subset='Musica').sort_values(by='Duracao').head(1)
        return df_filtrado.Artista.values[0] + ' - ' + df_filtrado.Musica.values[0] + ' (' + df_filtrado.Duracao_Formatada.values[0] + ')'

    def get_musica_maior_duracao(self):
        df_filtrado = self.df.dropna(subset='Musica').sort_values(by='Duracao').tail(1)
        return df_filtrado.Artista.values[0] + ' - ' + df_filtrado.Musica.values[0] + ' (' + df_filtrado.Duracao_Formatada.values[0] + ')'

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

    def get_musicas(self):
        df = self.df.sort_values(by='Data_Lancamento_Album')
        df = df.loc[:, ['Data_Lancamento_Album', 'Artista', 'Musica']].reset_index()
        df = df.rename(columns={"index": "unique_id", "Artista": "text", "Musica": "headline"})

        df['year'] = df['Data_Lancamento_Album'].dt.year
        df['month'] = df['Data_Lancamento_Album'].dt.month
        df['day'] = df['Data_Lancamento_Album'].dt.day
        df['start_date'] = df[['year', 'month', 'day']].to_dict(orient='records')
        df['text'] = df[['headline', 'text']].to_dict(orient='records')
        df = df.drop(['Data_Lancamento_Album','year', 'month', 'day', 'headline'], axis=1).to_dict(orient='records')

        return json.dumps({'events': df})

    def get_range_data_lancamento(self):
        return [(self.df.Data_Lancamento_Album.min() + pd.DateOffset(years=-3)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                (self.df.Data_Lancamento_Album.max() + pd.DateOffset(years=3)).strftime('%Y-%m-%dT%H:%M:%SZ')]

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

    def get_duracao(self):
        df_filtrado = self.df.dropna(subset='Musica').sort_values(by='Duracao')
        return [df_filtrado.head(1).Duracao_Formatada.values[0], df_filtrado.tail(1).Duracao_Formatada.values[0]]

#Inicialização
def load_data(agregar_pinkfloyd):
    df_data = pd.read_csv(dataset_file)
    df_data['Id'] = range(1, len(df_data) + 1)
    df_data['Edicao'] = df_data.Ano.astype(str).str[-2:] + "-" + (df_data.Ano +1).astype(str).str[-2:]
    df_data['Data_Lancamento_Album'] = pd.to_datetime(df_data['Data_Lancamento_Album'])
    df_data['Decada_Lancamento_Album'] = df_data['Data_Lancamento_Album'].dt.year.apply(get_decada)
    df_data['Duracao'] = df_data.loc[:,'Duracao'].fillna(value=0)
    df_data['Duracao_Formatada'] = df_data.apply(lambda row: time.strftime("%M:%S", time.gmtime(row['Duracao'])), axis=1)
    if (agregar_pinkfloyd):
        df_data.loc[df_data['Musica'].str.contains('Another Brick', na=False), 'Musica'] = 'Another Brick in the Wall'
        df_data.loc[df_data['Musica'].str.contains('Another Brick', na=False), 'Duracao'] = 508

    return df_data

#Funções
def get_decada(ano):
    return 'Anos ' + str(ano)[2] + '0'

def listar_edicoes(df_data):
    return np.array(np.unique(df_data.Edicao).tolist())

def listar_posicoes(df_data):
    return np.unique(df_data.Posicao).tolist()

def listar_anos_lancamento(df_data):
    return np.unique(df_data.Data_Lancamento_Album.dropna().dt.year.apply(lambda x: f'{x:.0f}')).tolist()

def listar_anos_edicoes(df_data):
    return np.array(np.unique(df_data.Ano).tolist())

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
    return df_data.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').head(1)['Data_Lancamento_Album'].dt.year

def get_ultimo_ano_lancamento(df_data):
    return df_data.dropna(subset=['Musica']).sort_values(by = 'Data_Lancamento_Album').tail(1)['Data_Lancamento_Album'].dt.year

def get_total_musicas_distintas(df_data):
    return len(get_musicas_distintas(df_data))

def get_total_artistas_distintos(df_data):
    return len(np.unique(df_data.Artista.dropna()).tolist())

def get_total_albuns_distintos(df_data):
    return len(np.unique(df_data.Album_Single.dropna().astype(str)).tolist())

def get_total_paises_distintos(df_data):
    return len(np.unique(df_data.Pais.dropna()).tolist())

def get_total_generos_distintos(df_data):
    return len(get_generos_distintos(df_data))

def get_musicas_distintas(df_data):
    return filtrar_inconsistencias(df_data).drop_duplicates(subset=['Artista', 'Musica', 'Observacao'])

def get_generos_distintos(df_data):
    return filtrar_inconsistencias(df_data).drop_duplicates(subset='Genero')

def get_total_horas(df_data):
    return np.sum(df_data.Duracao.dropna()) / 3600

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
    edicoes = np.unique(df_data.Edicao)
    edicao_inicial = edicoes[0]
    edicao_anterior = edicoes[len(edicoes) -2]
    df1 = get_top_n_musicas_media_posicao(df_data, top_n).reset_index()
    df2 = get_top_n_musicas_media_posicao(filtrar_edicao(df_data, edicao_inicial, edicao_anterior), 100).reset_index()

    merged_df = pd.merge(df1, df2, how='left', on = ['Artista', 'Musica'], suffixes=('_Atual', '_Anterior'))
    merged_df['Variacao'] = merged_df['Posicao_Anterior'] - merged_df['Posicao_Atual']

    return merged_df

def get_melhor_posicao_genero(df_data):
    df = df = df_data.sort_values('Ano')
    indexes = df.groupby(['Genero'])['Posicao'].idxmin()
    return df.loc[indexes, ['Genero', 'Posicao', 'Edicao']]

def get_analise_edicao(df_data, medida, analise):
    agregadores = {"Musica_Artista":['Artista', 'Edicao'],
                      "Album_Artista":['Album_Single', 'Edicao'],
                      "Musica_Genero":['Genero', 'Edicao'],
                      "Genero_Pais":['Pais','Edicao'],
                      "Duracao":['Duracao','Edicao']}

    dimensoes = {"Musica_Artista":'Musica',
                      "Album_Artista":'Musica',
                      "Musica_Genero":'Musica',
                      "Genero_Pais":'Genero',
                      "Duracao":'Duracao'}

    agregador = agregadores[analise]
    dimensao = dimensoes[analise]
    index_name = 'Contagem'

    df =  filtrar_inconsistencias(df_data)
    if (dimensao != 'Duracao'):
        df = df.groupby(agregador)[dimensao].count().reset_index(name=index_name)
    else:
        index_name = dimensao

    match medida:
        case 'Média':
            df = df.groupby('Edicao')[index_name].mean().reset_index(name=medida)
        case 'Mediana':
            df = df.groupby('Edicao')[index_name].median().reset_index(name=medida)
        case 'Máximo':
            df = df.groupby('Edicao')[index_name].max().reset_index(name=medida)
        case default:
            df = df

    if (dimensao == 'Duracao'):
        df[medida] = pd.to_datetime(df[medida], unit='s')

    return np.around(df,2)

def get_idade_por_edicao(df_data):
    df = df_data.copy()
    df = filtrar_inconsistencias(df)
    df['Idade_Lancamento'] = df['Ano'] + 1 - df['Data_Lancamento_Album'].dt.year

    df = df.loc[:,['Edicao', 'Idade_Lancamento']]
    df['Media_Idade_Lancamento'] = df.groupby('Edicao')['Idade_Lancamento'].transform('mean').round(2)
    df['Mediana_Idade_Lancamento'] = df.groupby('Edicao')['Idade_Lancamento'].transform('median').round(0)

    return df.groupby(['Edicao', 'Media_Idade_Lancamento', 'Mediana_Idade_Lancamento']).size().reset_index()

def get_grafico_linha(df_data, xdata, ydata1, xlabel, ylabel1, ydata2 = None, ylabel2 = None):
    fig = px.line()
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel1, separators=',.')
    fig.add_scatter(x=df_data[xdata], y=df_data[ydata1], name=ylabel1)
    if (ydata2 != None):
        fig.add_scatter(x=df_data[xdata], y=df_data[ydata2], name=ylabel2)
    fig.update_traces(hovertemplate=xlabel + ': %{x}<br> Valor: %{y}<extra></extra>')

    return fig

def get_grafico_barra(df_data, xdata, ydata, xlabel, ylabel, x_diagonal=False):
    fig = px.bar(df_data, x=xdata, y=ydata, text_auto=True)
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, separators=',.')
    fig.update_traces(marker_color='#C50B11', hovertemplate=xlabel + ": %{x}<br>" + ylabel + ": %{y}", textangle=0)
    if x_diagonal:
        fig.update_xaxes(tickangle=-45)
    if (df_data.select_dtypes(include=[np.datetime64]).columns.size > 0):
        fig.update_layout(yaxis_tickformat="%M:%S")
    
    return fig

def get_grafico_barra_horizontal(df_data, xdata, ydata, xlabel, ylabel, x_diagonal=False):
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

    return fig

def get_grafico_barra_stacked(df_data, xdata, ydata, ldata, xlabel, ylabel, llabel):
    fig = px.bar(df_data, x=xdata, y=ydata, color=ldata, color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, legend_title=llabel, legend_traceorder="reversed")
    fig.update_traces(hovertemplate='%{fullData.name}<br>' + xlabel + ": %{label}<br>" + ylabel + ": %{value}<extra></extra>")
    fig.update_xaxes(categoryorder='array', categoryarray=df_data.sort_values(xdata)[xdata].to_list())
    
    return fig

def get_grafico_pizza(df_data, valor, nomes, label_valor, label_nomes):
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
    
    return fig

def get_mapa(df_data):
    fig = px.choropleth(df_data, locationmode="country names", locations="Country", color='Total_Musicas', hover_name="Pais", color_continuous_scale=px.colors.sequential.YlOrRd, projection='natural earth')
    fig.update_layout(coloraxis_colorbar=dict(title="Quantidade de Músicas"))
    
    return fig

def get_mapa_calor(df_data):
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

    return fig

def get_analise_edicao_treemap(df_data, xdata, ydata, xlabel, ylabel):
    fig = px.treemap(df_data, path=[px.Constant('Todos'), xdata], values=ydata, color=xdata, hover_data=[xdata])
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.update_traces(hovertemplate=xlabel + ": %{label}<br>" + ylabel + ": %{value}")
    
    return fig

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
    return bcr.bar_chart_race(df_values, 
                            n_bars=10, 
                            steps_per_period=15, 
                            period_length=1000, 
                            title = titulo, 
                            period_template='{x:.0f}', 
                            bar_texttemplate='{x:.0f}', 
                            tick_template='{x:.0f}', 
                            fixed_max=True, 
                            filter_column_colors=True).data