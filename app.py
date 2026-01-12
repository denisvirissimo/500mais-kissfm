import json
import base64
import core_functions as core
import charts as ch
import components as components
from info import InfoEdicao, InfoMusica, InfoArtista, InfoCuriosidade
import locale
import streamlit as st
from streamlit_timeline import timeline

#Configuração
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
logo_file = './resources/logo.png'
icon_file = './resources/favicon.ico'
versao = '1.4.0'

def configurar_css():
    st.markdown(
    """
<style>
    [data-testid='stMetricDeltaIcon-Up'] {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

def plotar_grafico(fig):
    st.plotly_chart(fig, width="stretch")

def plotar_mapa_calor(fig):
    config = {'scrollZoom': False,
      'modeBarButtonsToRemove': [
          'zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale']}

    st.plotly_chart(fig, width="stretch", config = config)

def plotar_timeline(edicao):
    items = json.loads(edicao.get_musicas())

    options = {
        "start_at_end": False,
        "timenav_height": 50,
        "is_embed": True,
        "scale_factor": 11,
        "duration": 300,
        "language": "pt-br"
    }

    timeline(items, height=400, additional_options=options)

@st.cache_resource(show_spinner='Gerando gráfico de corrida...')
def plotar_grafico_race(df_data, atributo, titulo):
    html_data = ch.gerar_grafico_race(df_data, atributo, titulo)

    start = html_data.find('base64,') + len('base64,')
    end = html_data.find('">')

    video = base64.b64decode(html_data[start:end])
    st.video(video)

@st.cache_data
def load_data(agregar_pinkfloyd):
    return core.load_data(agregar_pinkfloyd)

@st.cache_data
def load_predicoes():
    return core.load_predicoes()

@st.cache_data
def get_dicionario_musicas(df_data):
    return core.get_dicionario_musicas(df_data)

@st.cache_data
def get_dicionario_artistas(df_data):
    return core.get_dicionario_artistas(df_data)

@st.cache_data
def show_data(df_data):
    st.dataframe(data=df_data.reset_index(drop=True), hide_index=True)

#App
st.set_page_config(layout="wide", 
                    page_title='As 500+ da Kiss',
                    page_icon=icon_file, 
                    menu_items={
                        'Get Help': 'https://github.com/denisvirissimo/500mais-kissfm',
                        'Report a bug': "https://github.com/denisvirissimo/500mais-kissfm/issues",
                        'About': '''Desenvolvido por [Denis Bruno Viríssimo](https://www.linkedin.com/in/denisbruno/)   
                        Versão {}'''.format(versao)
                    })

configurar_css()

if 'opt_pink_floyd' not in st.session_state:
    st.session_state.opt_pink_floyd = True

df_listagem = load_data(st.session_state.opt_pink_floyd)
df_predicoes = load_predicoes()

list_analises_edicao = {"Músicas por Artista":'Musica_Artista', "Álbuns por Artista":'Album_Artista', "Músicas por Gênero":'Musica_Genero', "Gêneros por País":'Genero_Pais', "Duração":'Duracao'}
list_variaveis_topn = {"Artista": 'Artista', "Música": 'Musica', "Álbum/Single": 'Album', "Gênero": 'Genero', "Artistas com músicas em posições similares": 'Artista_Posicao'}
medidas = ["Média", "Mediana", "Máximo"]


#Sidebar
st.sidebar.subheader('Filtros')
st.sidebar.text('')

#Filtro Edições
edicoes = core.listar_edicoes(df_listagem)
edicao_inicial, edicao_final = st.sidebar.select_slider('Filtrar por edições', edicoes, value = [core.get_primeira_edicao(df_listagem).values[0], core.get_ultima_edicao(df_listagem).values[0]])
df_listagem_filtrada = core.filtrar_edicao(df_listagem, edicao_inicial, edicao_final)

#Filtro Posições
posicoes = core.listar_posicoes(df_listagem)
posicao_inicial, posicao_final = st.sidebar.select_slider('Filtrar por posições', posicoes, value=[min(posicoes), max(posicoes)])
df_listagem_filtrada = core.filtrar_posicoes(df_listagem_filtrada, posicao_inicial, posicao_final)

#Filtro Ano Lançamento
anos = core.listar_anos_lancamento(df_listagem)
ano_inicial, ano_final = st.sidebar.select_slider('Filtrar por anos de lançamento das músicas', anos, value=[min(anos), max(anos)])
df_listagem_filtrada = core.filtrar_anos(df_listagem_filtrada, ano_inicial, ano_final)

st.sidebar.caption('Estes filtros se aplicam somente às abas Visão Geral e Análises.')

st.sidebar.subheader('Opções')

st.sidebar.toggle('Agregar múltiplas versões de Another Brick in the Wall', key='opt_pink_floyd', help='[Clique aqui](https://github.com/denisvirissimo/500mais-kissfm#o-caso-de-another-brick-in-the-wall) para entender.')

col1, col2, col3 = st.columns((.2, 7.1, .2))

with col2:
    row_titulo_col1, row_titulo_col2 = st.columns((.25, 3.3), gap="small")
    with row_titulo_col1:
        st.image(logo_file, width=75)
    with row_titulo_col2:
        st.title('As 500+ da Kiss FM')

    st.markdown("Esse é um projeto de Ciência de Dados com o objetivo de analisar a listagem das 500+ da rádio Kiss FM. A ideia surgiu a partir da curiosidade de saber qual seria a música número 1 de todas as votações até então, e acabou levando ao desenvolvimento de várias outras análises interessantes.")
    st.markdown("Todo o detalhamento do projeto, inclusive o tratamento de dados e algumas curiosidades, está disponível neste [repositório do GitHub](https://github.com/denisvirissimo/500mais-kissfm)")

    st.markdown("")
    with st.status("Carregando...") as status:
        show_data(df_listagem)
        status.update(label="Clique aqui para ver a listagem completa", state="complete")

    st.text('')
    st.subheader("Exibindo os seguintes dados a partir dos filtros:")

    row_numeros_col1, row_numeros_col2, row_numeros_col3, row_numeros_col4, row_numeros_col5, row_numeros_col6, row_numeros_col7 = st.columns((1.6, 1.6, 1.0, 1.5, 1.6, 1.4, 1.1), gap="small")
    with row_numeros_col1:
        total_musicas = df_listagem_filtrada.Id.nunique()
        str_total_musicas = "🎶 {} músicas no total".format(locale.format_string("%d", total_musicas, grouping = True))
        st.markdown(str_total_musicas)
    with row_numeros_col2:
        total_musicas_distintas = core.get_total_musicas_distintas(df_listagem_filtrada)
        str_total_musicas_distintas = "🎵 {} músicas diferentes".format(locale.format_string("%d", total_musicas_distintas, grouping = True))
        st.markdown(str_total_musicas_distintas)
    with row_numeros_col3:
        total_artistas = core.get_total_artistas_distintos(df_listagem_filtrada)
        str_total_artistas = "👨🏽‍🎤 {} artista(s)".format(locale.format_string("%d", total_artistas, grouping = True))
        st.markdown(str_total_artistas)
    with row_numeros_col4:
        total_albuns = core.get_total_albuns_distintos(df_listagem_filtrada)
        str_total_albuns = "💿 {} álbum(s)/single(s)".format(locale.format_string("%d", total_albuns, grouping = True))
        st.markdown(str_total_albuns)
    with row_numeros_col5:
        total_paises = core.get_total_paises_distintos(df_listagem_filtrada)
        str_total_paises = "🌎 {} países representados".format(locale.format_string("%d", total_paises, grouping = True))
        st.markdown(str_total_paises)
    with row_numeros_col6:
        total_generos = core.get_total_generos_distintos(df_listagem_filtrada)
        str_total_generos = "🤘 {} gêneros musicais".format(locale.format_string("%d", total_generos, grouping = True))
        st.markdown(str_total_generos)
    with row_numeros_col7:
        total_horas = core.get_total_horas(df_listagem_filtrada)
        str_total_horas = "🕛 {}+ horas".format(locale.format_string("%d", total_horas, grouping = True))
        st.markdown(str_total_horas)

    st.divider()

    tab_geral, tab_edicao, tab_edicoes, tab_analises, tab_curiosidades, tab_predicoes = st.tabs(["Visão Geral", "Por Edição", "Todas as Edições", "Análises", "Curiosidades", "Predições"])

    with tab_geral:
        st.subheader('Evolução de músicas distintas ao longo dos anos')
        plotar_grafico(ch.get_grafico_barra(core.get_acumulado_musicas_distintas(df_listagem_filtrada), "Anos", "Acumulado", "Edições", "Acumulado de Músicas distintas"))

        st.divider()

        st.subheader('Evolução de gêneros musicais distintos ao longo dos anos')
        plotar_grafico(ch.get_grafico_barra(core.get_acumulado_generos_distintos(df_listagem_filtrada), "Anos", "Acumulado", "Edições", "Acumulado de Gêneros Musicais distintos"))

        st.divider()

        st.subheader('Artistas, Músicas, Álbuns e Gêneros no Topo')

        row_topn_col1, row_topn_col2 = st.columns((2, 5), gap="large")
        with row_topn_col1:
            top_n = st.slider('Qual Top N você deseja visualizar?', 1, 50, 3)
            variavel_topn_selecionada = st.selectbox ("Escolha a variável para visualizar no Top", list(list_variaveis_topn.keys()), key = 'variavel_topn')
            if (list_variaveis_topn[variavel_topn_selecionada] == 'Artista_Posicao'):
                st.caption('Considera-se música em posição similar aquela com uma variação de até 5 posições (para mais ou para menos)')
        with row_topn_col2:
            match list_variaveis_topn[variavel_topn_selecionada]:
                case 'Artista':
                    st.dataframe(data=core.get_artistas_top_n(df_listagem_filtrada, top_n), hide_index=True, width="stretch", height=400, column_config={"Artista":"Artista", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Musica':
                    st.dataframe(data=core.get_musicas_top_n(df_listagem_filtrada, top_n), hide_index=True, width="stretch", height=400, column_config={"Musica":"Música", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Album':
                    st.dataframe(data=core.get_albuns_top_n(df_listagem_filtrada, top_n), hide_index=True, width="stretch", height=400, column_config={"Album_Single":"Álbum/Single", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Genero':
                    st.dataframe(data=core.get_generos_top_n(df_listagem_filtrada, top_n), hide_index=True, width="stretch", height=400, column_config={"Genero":"Gênero", "Total_Aparicoes": "Número Total de Aparições"})
                case 'Artista_Posicao':
                    st.dataframe(data=core.get_artistas_posicoes_semelhantes_top_n(df_listagem_filtrada, top_n), hide_index=True, width="stretch", height=400, column_config={"Artista": "Artista", "Posicao_Semelhante": st.column_config.NumberColumn("Porcentagem de vezes em posições similares", format="percent")})
                case default:
                    st.write('Escolha uma opção')

        st.divider()

        st.subheader('Músicas distintas por Ano de Lançamento')
        plotar_grafico(ch.get_grafico_barra(core.get_musicas_ano_lancamento(df_listagem_filtrada), "Data_Lancamento_Album", "Total_Musicas", "Anos", "Quantidade de Músicas distintas", True))

        st.divider()

        st.subheader('Músicas distintas por Década de Lançamento')
        plotar_grafico(ch.get_grafico_barra(core.get_musicas_decada_lancamento(df_listagem_filtrada), "Decada_Lancamento_Album", "Total_Musicas", "Décadas", "Quantidade de Músicas distintas"))

        st.divider()

        st.subheader('Músicas distintas por País do Artista')
        plotar_grafico(ch.get_grafico_barra_stacked(core.get_musicas_por_pais(df_listagem_filtrada), "Edicao", "Total_Musicas", "Pais", "Edições", "Músicas por País", "Países"))

        st.divider()

        st.subheader('Músicas distintas por Gênero Musical do Artista')
        plotar_grafico(ch.get_grafico_barra_stacked(core.get_musicas_por_genero(df_listagem_filtrada), "Edicao", "Total_Musicas", "Genero", "Edições", "Músicas por Gênero Musical", "Gêneros Musicais"))

        st.divider()

        row_posicaogenero, row_paises = st.columns((3.5, 3.5), gap="large")
        with row_posicaogenero:
            st.subheader('Melhor posição de cada gênero')
            st.dataframe(data=core.get_melhor_posicao_genero(df_listagem_filtrada), hide_index=True, width="stretch", height=400, column_config={"Genero":"Gênero", "Posicao": "Melhor Posição", "Edicao": "Edição"})

        with row_paises:
            st.subheader('Mapa de Países')
            plotar_grafico(ch.get_mapa(core.get_musicas_por_pais(df_listagem_filtrada, True), "Country", "Total_Musicas", "Pais", "Quantidade de Músicas"))

    with tab_edicao:

        st.markdown('Escolha uma edição e veja algumas informações relavantes:')

        row_edicoes_col1, row_edicoes_col2= st.columns((1.5, 6.2), gap="small")
        with row_edicoes_col1:
            anos = core.listar_anos_edicoes(df_listagem)
            list_edicoes = dict(zip(edicoes, anos))
            edicao_selecionada = st.selectbox ("Edição", list_edicoes.keys(), key = 'edicao_selecionada')

        ano_edicao = list_edicoes[edicao_selecionada]
        info_edicao = InfoEdicao(df_listagem, ano_edicao)
        st.divider()

        st.subheader("Linha do tempo das músicas na edição")
        plotar_timeline(info_edicao)

        st.caption('Use os as setas ao lado para avançar/retornar na linha do tempo. Clique e arraste na linha para avançar um período maior.')

        st.divider()
        row_dadosedicao_col1, row_dadosedicao_col2, row_dadosedicao_col3 = st.columns((1.2, 2.6, 2.6), gap="large")

        with row_dadosedicao_col1:
            st.subheader('Dados Gerais')


            st.markdown('Neste ano a 1ª posição ficou com **{}** e a posição de número 500 com **{}**.'.format(info_edicao.get_musica_posicao(1), info_edicao.get_musica_posicao(500)))

            st.markdown('O Artista em que mais apareceu na listagem foi **{}**.'.format(info_edicao.get_top_artista()))
            st.markdown('Já o Álbum/Single com mais músicas na lista foi **{}**.'.format(info_edicao.get_top_album()))

            st.markdown('O Gênero Musical mais tocado foi **{}**.'.format(info_edicao.get_top_genero()))

            st.markdown('A Música de menor duração foi **{}** e a música de maior duração foi **{}**'.format(info_edicao.get_musica_menor_duracao(), info_edicao.get_musica_maior_duracao()))

            st.markdown('E tivemos música repetida? **{}**!'.format(info_edicao.get_repetidas()))

        with row_dadosedicao_col2:
            st.subheader('Países dos Artistas na Edição')
            plotar_grafico(ch.get_grafico_pizza(info_edicao.get_lista_paises(), 'Quantidade', 'Pais', 'Músicas', 'País'))

        with row_dadosedicao_col3:
            st.subheader('Gêneros Musicais na Edição')
            plotar_grafico(ch.get_grafico_pizza(info_edicao.get_lista_generos(), 'Quantidade', 'Genero', 'Músicas', 'Gênero Musical'))

        st.divider()
        if (ano_edicao != anos[0]):
            row_edicaosubidas, row_edicaoquedas = st.columns((3.5, 3.5), gap="large")

            with row_edicaosubidas:
                st.subheader('Maiores subidas no ranking')
                plotar_grafico(ch.get_grafico_slope(core.get_variacao_entre_anos(df_listagem, ano_edicao -1, ano_edicao, 5, False), 'Ano', ano_edicao - 1, ano_edicao, 'Posicao_Anterior', 'Posicao_Atual', 'Musica', 'Artista', 'Variaçãos no Ranking'))

            with row_edicaoquedas:
                st.subheader('Maiores quedas no ranking')
                plotar_grafico(ch.get_grafico_slope(core.get_variacao_entre_anos(df_listagem, ano_edicao -1, ano_edicao, 5, True), 'Ano', ano_edicao - 1, ano_edicao, 'Posicao_Anterior', 'Posicao_Atual', 'Musica', 'Artista', 'Variaçãos no Ranking'))

            st.divider()

        st.subheader('Mapa de Gêneros Músicais')
        plotar_grafico(ch.get_analise_edicao_treemap(info_edicao.get_lista_generos(), 'Genero', 'Quantidade', 'Gênero', 'Quantidade de Músicas'))

    with tab_analises:
        st.subheader('Análises por edição')
        st.markdown('A análise de alguns aspectos por edição pode mostrar a diversidade de músicas, álbuns e gêneros musicais a cada edição.')
        row_anelisemusica_col1, row_anelisemusica_col2 = st.columns((1.5, 6.2), gap="small")
        with row_anelisemusica_col1:
            analisemusica_edicao_selecionada = st.selectbox("Escolha o aspecto", list(list_analises_edicao.keys()), key = 'analise_edicao')
            analisemusica_medida_selecionada = st.selectbox("Escolha a medida", medidas, key = 'medida_edicao')
        with row_anelisemusica_col2:
            plotar_grafico(ch.get_grafico_barra(core.get_analise_edicao(df_listagem_filtrada, analisemusica_medida_selecionada, list_analises_edicao[analisemusica_edicao_selecionada]),
                                "Edicao",
                                analisemusica_medida_selecionada,
                                "Edições",
                                analisemusica_medida_selecionada + ' de ' + analisemusica_edicao_selecionada))

        st.divider()
        st.subheader('One-Hit Wonders vs Recorrentes')
        st.markdown('A análise de artistas que tiveram somente uma única música diferente em edições até hoje vs artistas que tiveram pelo menos duas músicas diferentes ajuda a compreender a preferência dos ouvintes')
        plotar_grafico(ch.get_grafico_linha(core.get_onehit_por_edicao(df_listagem_filtrada), 'Edicao', 'Recorrentes', 'Edições', 'Artistas', 'Recorrentes', 'One_Hit_Wonders', 'One-Hit Wonders'))

        st.divider()
        st.subheader('Idade das músicas')
        st.markdown('A análise de idade das músicas demonstra se há uma tradição de votação em músicas mais antigas (especialmente da década de 70) ou se têm sido incorporadas músicas mais recentes na listagem.')
        st.markdown('A idade é recalculada a cada edição.')

        plotar_grafico(ch.get_grafico_linha(core.get_idade_por_edicao(df_listagem_filtrada), 'Edicao', 'Media_Idade_Lancamento', 'Edições', 'Idade', 'Média de Idade', 'Mediana_Idade_Lancamento', 'Mediana de Idade'))

    with tab_curiosidades:

        info_curiosidades = InfoCuriosidade(core.filtrar_inconsistencias(df_listagem))

        curiosidade = info_curiosidades.get_primeiro_artista_br()
        st.markdown('* A primeira aparição de um artista brasileiro foi em {} com {}, ficando na {}ª posição.'.format(curiosidade[1], curiosidade[0], curiosidade[2]))

        curiosidade = info_curiosidades.get_edicao_menos_artistas()
        st.markdown('* A edição com menos artistas foi a {}, contando com "apenas" {} artistas.'.format(curiosidade[0], curiosidade[1]))

        curiosidade = info_curiosidades.get_edicao_mais_artistas()
        st.markdown('* Já a edição com mais artistas foi a {}, com {} artistas.'.format(curiosidade[0], curiosidade[1]))

        curiosidade = info_curiosidades.get_artista_mais_musicas_edicao()
        st.markdown('* O recorde de mais músicas em uma única edição é de {} com impressionantes {} músicas na edição {}.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

        curiosidade = info_curiosidades.get_one_hit_wonder()
        st.markdown('* {} ({}%) artistas aparceram nas edições com uma única música (os chamados "one-hit wonders")'.format(curiosidade[0], curiosidade[1]))
        
        curiosidade = info_curiosidades.get_album_mais_musicas_edicao()
        st.markdown('* O álbum/single com mais músicas em uma única edição é {} com {} músicas na edição {}.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

        curiosidade = info_curiosidades.get_album_mais_musicas()
        st.markdown('* O álbum/single com mais músicas em todas as edições é {} de {}, com {} músicas. Isto representa {} % de todas as músicas.'.format(curiosidade[1], curiosidade[0], curiosidade[2], curiosidade[3]))

        curiosidade = info_curiosidades.get_duracao()
        st.markdown('* A música com menor duração teve {} e a música com maior duração {}.'.format(curiosidade[0], curiosidade[1]))

        curiosidade = info_curiosidades.get_artista_maior_percentual()
        st.markdown('* {} é o artista com maior número de músicas: {}, o que representa {} % do total de músicas.'.format(curiosidade[0], curiosidade[1], curiosidade[2]))

    with tab_predicoes:
        row_predicoes_col1, row_predicoes_col2 = st.columns((3, 3.5), gap="small")

        with row_predicoes_col1:
            st.subheader('Predições das 500+ para {}'.format(max(anos)+1))
            st.dataframe(core.get_predicoes(df_predicoes), hide_index=True, column_config={"posicao_ranking": st.column_config.Column("Posição", width=1), "Artista": "Artista", "Musica": "Música"})

        with row_predicoes_col2:
            st.subheader('Probabilidades da música aparecer em {}'.format(max(anos)+1))
            st.dataframe(core.get_probabilidades(df_predicoes), hide_index=True, column_config={"Artista": "Artista", "Musica": "Música", "prob_aparecer": st.column_config.NumberColumn("Probabildiade de Aparecer", format="%.2f %%")})

    with tab_edicoes:

        rwo_ranking, row_videos= st.columns((3.8, 3.8), gap="small")

        with rwo_ranking:
            st.subheader('Top 10 de todas as edições')
            components.top10(core.get_top_n_todas_edicoes(df_listagem, 10))
            st.caption('Para entender como essa lista foi criada, consulte [a explicação](https://github.com/denisvirissimo/500mais-kissfm#as-maiores-de-todos-os-tempos).')
        st.divider()

        st.subheader('Mapa de calor de músicas presentes em todas as edições')
        plotar_mapa_calor(ch.get_mapa_calor(core.get_musicas_todos_anos(df_listagem), "Edição", "Música", "Posição", "Edições", "Músicas"))

        st.divider()

        row_anelisemusica_col1, row_anelisemusica_col2= st.columns((3.5, 4.1), gap="small")
        with row_anelisemusica_col1:
            st.subheader('Informações da música')

            lista_select_musicas = get_dicionario_musicas(df_listagem)
            musica_selecionada = st.selectbox(
              'Escolha a música',
              label_visibility='hidden',
              options=lista_select_musicas.keys(),
              index=None,
              placeholder='Digite ou escolha a música',
              format_func=lambda l: lista_select_musicas[l])

            st.text('')

        if (musica_selecionada != None):
            row_infomusica_col1, row_infomusica_col2, row_infomusica_col3, row_infomusica_col4 = st.columns(4)
            info_musica = InfoMusica(core.filtrar_inconsistencias(df_listagem), musica_selecionada)
            row_infomusica_col1.metric(label="📈 Melhor Posição", value=str(info_musica.get_melhor_posicao()) + 'ª', delta=info_musica.get_edicao_melhor_posicao(), delta_color='off')
            row_infomusica_col2.metric(label="📉 Pior Posição", value=str(info_musica.get_pior_posicao()) + "ª", delta=info_musica.get_edicao_pior_posicao(), delta_color='off')
            row_infomusica_col3.metric(label="📊 Posição Média", value=str(info_musica.get_posicao_media()) + "ª")
            row_infomusica_col4.metric(label="🗓️ Década", value=info_musica.get_decada())
            st.text('')
            row_infomusica_col5, row_infomusica_col6, row_infomusica_col7, row_infomusica_col8= st.columns(4)
            row_infomusica_col5.metric(label="#️⃣ Número Aparições", value=info_musica.get_numero_aparicoes())
            row_infomusica_col6.metric(label='🔥 Aparições Consecutivas', value=info_musica.get_numero_aparicoes_consecutivas())
            row_infomusica_col7.metric(label='🏅 Número Pódios', value=info_musica.get_numero_podios())
            row_infomusica_col8.metric(label='🏅 Pódios Consecutivos', value=info_musica.get_numero_podios_consecutivos())

            st.subheader('Histórico')
            plotar_grafico(ch.get_grafico_linha(info_musica.get_posicoes(),'Ano', 'Posicao', 'Ano', 'Posição no ranking', '', reversed=True))

        st.divider()

        row_aneliseartista_col1, row_aneliseartista_col2= st.columns((3.5, 4.1), gap="small")
        with row_aneliseartista_col1:
            st.subheader('Informações do artista')

            lista_select_artistas = get_dicionario_artistas(df_listagem)
            artista_selecionado = st.selectbox(
                'Escolha o artista',
                label_visibility='hidden',
                options=lista_select_artistas.keys(),
                index=None,
                placeholder='Digite ou escolha o artista',
                format_func=lambda l: lista_select_artistas[l])

            st.text('')

        if (artista_selecionado != None):
            row_infoartista_col1, row_infoartista_col2, row_infoartista_col3, row_infoartista_col4 = st.columns(4)
            info_artista = InfoArtista(core.filtrar_inconsistencias(df_listagem), artista_selecionado)
            row_infoartista_col1.metric(label="📈 Melhor Posição", value=str(info_artista.get_melhor_posicao()) + 'ª', delta=info_artista.get_edicao_melhor_posicao(), delta_color='off')
            row_infoartista_col2.metric(label="📉 Pior Posição", value=str(info_artista.get_pior_posicao()) + "ª", delta=info_artista.get_edicao_pior_posicao(), delta_color='off')
            row_infoartista_col3.metric(label="🎶 Total Músicas", value=info_artista.get_total_musicas())
            row_infoartista_col4.metric(label="️#️⃣ Número Edições", value=info_artista.get_total_edicoes())
            st.text('')
            row_infoartista_col5, row_infoartista_col6, row_infoartista_col7, row_infoartista_col8= st.columns(4)
            row_infoartista_col5.metric(label="️🎵Média Músicas", value=locale.format_string("%.2f", info_artista.get_media_musicas_por_edicao(), grouping = True), delta="por edição", delta_color='off')
            row_infoartista_col6.metric(label='🔥 Aparições Consecutivas', value=info_artista.get_numero_aparicoes_consecutivas())
            row_infoartista_col7.metric(label='🏅 Número Pódios', value=info_artista.get_numero_podios())
            row_infoartista_col8.metric(label='🏅 Pódios Consecutivos', value=info_artista.get_numero_podios_consecutivos())

        with row_videos:

            st.subheader('')
            plotar_grafico_race(core.get_dados_cumulativos(load_data(False), 'Artista'),
                              'Artista',
                              'Top 10 Artistas com mais músicas nas edições')

            plotar_grafico_race(core. get_dados_cumulativos(load_data(False), 'Genero'),
                              'Genero',
                              'Top 10 Gêneros Musicais com mais músicas nas edições')