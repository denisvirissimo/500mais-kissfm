import pandas as pd
import numpy as np
import locale

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

#Inicialização
df_listagem = pd.read_csv("/content/sample_data/500+.csv")
df_listagem['Id'] = range(1, len(df_listagem) + 1)
df_listagem['Ano_Periodo'] = df_listagem.Ano.astype(str).str[-2:] + "-" + (df_listagem.Ano +1).astype(str).str[-2:]

total_musicas = df_listagem.Id.nunique()
str_total_musicas = "🎶 " + locale.format_string("%d", total_musicas, grouping = True) + " músicas no total"

total_musicas_distintas = len(np.unique(df_listagem.Musica.astype(str)).tolist())
str_total_musicas_distintas = "🎵 " + locale.format_string("%d", total_musicas_distintas, grouping = True) + " músicas diferentes"

total_artistas = len(np.unique(df_listagem.Artista).tolist())
str_total_artistas = "🧑‍🎤 " + locale.format_string("%d", total_artistas, grouping = True) + " artista(s)"

total_albuns = len(np.unique(df_listagem.Album_Single.astype(str)).tolist())
str_total_albuns = "💿 " + locale.format_string("%d", total_albuns, grouping = True) + " álbum(s)/single(s)"