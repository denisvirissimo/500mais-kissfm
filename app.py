import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import locale

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

#Inicialização
df_listagem = pd.read_csv("./data/500+.csv")
df_listagem['Id'] = range(1, len(df_listagem) + 1)
df_listagem['Ano_Periodo'] = df_listagem.Ano.astype(str).str[-2:] + "-" + (df_listagem.Ano +1).astype(str).str[-2:]
df_listagem['Data_Lancamento_Album'] = pd.to_datetime(df_listagem['Data_Lancamento_Album'])

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
  return len(df_data.loc[(df_data['Artista'] != '???') & (df_data['Musica'].str.len() > 0), ['Artista', 'Musica']].drop_duplicates())

def get_acumulado_musicas_distintas(df_data):
  periodos = np.unique(df_data.Ano_Periodo).tolist()
  distinta_acumulado_periodo = []
  for p in periodos:
    distinta_acumulado_periodo.append(get_total_musicas_distintas(filtrar_periodo(df_listagem, periodos[0], p)))
  return pd.DataFrame({'Anos': periodos, 'Acumulado': distinta_acumulado_periodo})

# App
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

array = get_acumulado_musicas_distintas(df_listagem)

rc = {'figure.figsize':(8,4.5),
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

ax = sb.barplot(x="Anos", y="Acumulado", data=array, color = "#b80606")
ax.set(xlabel = "Anos", ylabel = "Acumulado de Músicas distintas")
plt.xticks(rotation=66,horizontalalignment="right")
for p in ax.patches:
    ax.annotate(format(str(int(p.get_height()))),
          (p.get_x() + p.get_width() / 2., p.get_height()),
            ha = 'center',
            va = 'center',
            xytext = (0, 18),
            rotation = 90,
            textcoords = 'offset points')
plt.show()