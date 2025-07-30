import json
import pandas as pd
import numpy as np

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

    def __listar_podios(self, df):
        return df[df['Posicao'].isin({1,2,3})]
    
    def __contar_consecutivos(self, df):
        df = df.reset_index()
        diff = df['Ano'] + df.index
        return df.groupby(diff)['Ano'].size().max()

    def get_melhor_posicao(self):
        return np.min(self.df.Posicao)

    def get_pior_posicao(self):
        return np.max(self.df.Posicao)

    def get_numero_aparicoes(self):
        return np.size(self.df.Posicao)
    
    def get_numero_aparicoes_consecutivas(self):        
        return self.__contar_consecutivos(self.df)
    
    def get_numero_podios(self):
        return np.size(self.__listar_podios(self.df)['Musica'])
    
    def get_numero_podios_consecutivos(self):
        return np.nan_to_num(self.__contar_consecutivos(self.__listar_podios(self.df))).astype('int')

    def get_decada(self):
        return self.df.Decada_Lancamento_Album.values[0]

    def get_posicao_media(self):
        return np.mean(self.df.Posicao).round(0).astype(int)
    
    def get_edicao_melhor_posicao(self):
        return "Edição " + self.df[self.df['Posicao'] == self.get_melhor_posicao()].Edicao.values[-1]
    
    def get_edicao_pior_posicao(self):
        return "Edição " + self.df[self.df['Posicao'] == self.get_pior_posicao()].Edicao.values[-1]

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