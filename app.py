import pandas as pd
import numpy as np
import locale

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

#Inicialização
df_listagem = pd.read_csv("./data/500+.csv")
df_listagem['Id'] = range(1, len(df_listagem) + 1)
df_listagem['Ano_Periodo'] = df_listagem.Ano.astype(str).str[-2:] + "-" + (df_listagem.Ano +1).astype(str).str[-2:]

#Funções
def filtrar_periodo(df_data, periodo_inicial, periodo_final):
  df_periodo_filtrado = pd.DataFrame()
  periodos = np.unique(df_data.Ano_Periodo).tolist()
  indice_inicial = periodos.index(periodo_inicial)
  indice_final = periodos.index(periodo_final)+1
  periodos_selecionados = periodos[indice_inicial:indice_final]
  return df_data[df_data['Ano_Periodo'].isin(periodos_selecionados)]

def filtrar_posicoes(df_data, posicao_inicial, posicao_final):
  df_posicoes_filtrado = pd.DataFrame()
  posicoes = list(range(posicao_inicial, posicao_final + 1))
  return df_data[df_data['Posicao'].isin(posicoes)]


# App
df_listagem_filtrada = filtrar_periodo(df_listagem, '00-01', '23-24')
df_listagem_filtrada = filtrar_posicoes(df_listagem_filtrada, 1, 500)

total_musicas = df_listagem_filtrada.Id.nunique()
total_musicas_distintas = len(df_listagem_filtrada.loc[(df_listagem_filtrada['Artista'] != '???') & (df_listagem_filtrada['Musica'].str.len() > 0), ['Artista', 'Musica']].drop_duplicates())
total_artistas = len(np.unique(df_listagem_filtrada.Artista.dropna()).tolist())
total_albuns = len(np.unique(df_listagem_filtrada.Album_Single.dropna().astype(str)).tolist())

str_total_musicas = "🎶 " + locale.format_string("%d", total_musicas, grouping = True) + " músicas no total"
str_total_musicas_distintas = "🎵 " + locale.format_string("%d", total_musicas_distintas, grouping = True) + " músicas diferentes"
str_total_artistas = "🧑‍🎤 " + locale.format_string("%d", total_artistas, grouping = True) + " artista(s)"
str_total_albuns = "💿 " + locale.format_string("%d", total_albuns, grouping = True) + " álbum(s)/single(s)"