import pandas as pd
import numpy as np
import io
import time

#Configuração
pd.set_option("styler.render.max_elements", 350000)
dataset_file = './data/500+.csv'

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

def get_dados_cumulativos(df_data, atributo):
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

    return df_data