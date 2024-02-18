# 500mais-kissfm
Projeto de DataScience da lista das 500 mais da Kiss FM.

# Tratamento de dados

Antes da análise dos dados relativos à todos os anos das 500+ da Kiss FM foi necessário agrega-los. Os itens a seguir descrevem todo esse processo. 
A maior parte dele foi automatizada, porém em alguns momentos uma intervenção manual foi necessária. Dessa forma, eventuais erros podem ter sido introduzidos na listagem, já que a conferência final foi feita por amostragem. Assim sendo, reporte qualquer inconsistência por meio das issues do repositório.

## Ferramentas utitlizadas

* Microsoft Excel
* OpenRefine 3.7.7
* Wikidata Reconciliation Service
* Wikidata API

Projeto do OpenRefine está disponível neste [arquivo](../main/data/500%2B_openrefine.tar.gz).

## Coleta

Os dados foram coletados a partir das <a href="#fontes">fontes</a> listadas, na ordem em que foram elencadas. Em alguns casos foi realizada uma referência cruzada das informações das fontes para tirar dúvidas sobre as informações das músicas, posições, álbuns, etc.
Nesta etapa todo o trabalho foi realizado utilizando o Excel e o resultado final foi compilado no [arquivo raw](../main/data/raw/500%2B_raw.xlsx).
Após isso foi gerada uma planilha com todas as 12.000 músicas (até o momento, compreendendo os anos 2000-2023) para início do processo de tratamento.

## Tratamento e clusterização

Para a limpeza e tratamento dos dados a planilha com todas as músicas foi importada no OpenRefine. A partir daí, algumas adequações e ajustes foram necessários para padronizar os dados, descritos a seguir.

A padronização e unificação dos nomes foi realizado por meio dos métodos de [clustering do OpenRefine](https://openrefine.org/docs/technical-reference/clustering-in-depth). Foram utilizados diversos métodos até que fosse possível ter o mínimo possível de duplicatas. Ainda assim, alguma revisão manual foi realizada. 

### Posição

O tratamento dos dados de posição das <a href="#outras-considerações">músicas não identificadas</a> precisou de cruzamento das listagens das 500+ de algumas fontes. Em caso de conflitos entre 2 listas diferentes, optou-se por permanecer com os dados da lista mais recente.

### Artista

Os nomes dos artistas e bandas foram padronizados, agregando itens que estavam com diversos formatos (maiúsculo, minúsculo, com erros de grafia, etc.). Após isto foram analisados os casos específicos de colaboração, participação e junção de diferentes artistas em uma música.

Para as colaborações optou-se por manter a junção por meio de conectivos, tais como "and", "&" ou "e". Isto foi orientado por uma rápida pesquisa na Wikipedia.

As participações (conhecidas como "featuring") foram removidas do nome do artista e registradas em um novo campo "Observacao" no arquivo final (também utilizado para informações da música em si).

### Música

Os nomes das músicas também foram padronizados, agregando itens que estavam com diversos formatos (maiúsculo, minúsculo, com erros de grafia, etc.). Após isto foram analisados os casos específicos de "tipos" de músicas.

Diversas observações foram realizadas para esses "tipos" de músicas, tais como "ao vivo", "acústica", ou alguma outra versão específica. Para músicas "ao vivo" e "acústica" em específico, essa observação norteou a escolha do álbum (descrito na próxima seção).

Além disso, foi registrado também se a música foi repetida na lista daquele ano (ocorreram 32 vezes ao longo desses 24 anos). Nas fontes consultadas já havia a indicação de que algumas músicas estavam repetidas, o que leva a crer que não foi um erro de digitação de quem registrou a informação, mas sim uma falha na programação da própria Kiss. Neste caso, foi anotado no campo "observação" como "repetida", na música da posição mais baixa (ou seja, quando ela efetivamente foi repedita na reprodução).

### Álbum/Single

Optou-se pela escolha não somente de álbuns, mas também de singles como obra principal em que a música aparece. Assim sendo, a obra com data de lançamento mais antiga foi escolhida.

No caso de músicas com observações, tais como "ao vivo" e "acústica" foi escolhido o primeiro álbum/single em que uma versão assim aparece.

Como fonte de informação para checagem manual das datas de lançamento do álbum/single, o seguintes sites foram consultados, prevalecendo também a data mais antiga de lançamento encontrada:

1. Wikipedia
2. Rate Your Music
3. Discogs

Em alguns casos, apenas o ano (ou mês e ano) do lançamento foi identificado. Dessa forma, o registro foi marcado com o dia 01 de janeiro (ou do mês indicado) do respectivo ano. Ex:

* Álbum lançado em ??/??/1956 -> Data de lançamento 01/01/1956
* Álbum lançado em ??/12/1956 -> Data de lançamento 01/12/1956

Todos os álbuns têm pelo menos o ano preenchido corretamente.

Considerando que neste momento a análise dos dados neste projeto de DataScience será focada somente no ano, não haverá prejuízo. A busca por essa informação seguirá em andamento para refinar os dados. 

## Reconciliação (via Wikidata)

Boa parte do processo de tratamento de dados foi automatizado por meio da funcionalidade de [reconciliação](https://openrefine.org/docs/manual/reconciling) do OpenRefine e o respectivo serviços da Wikidata.

Ao reconciliar os dados de artistas, músicas e álbuns com dados da Wikipedia foi possível validar as informações com confiabilidade. A reconciliação automática obteve os seguintes resultados:
* Artistas: 98,33%
* Músicas: 90%
* Álbuns/Singles: 95%

No caso dos Artistas, aqueles que possuem algum tipo de colaboração nas músicas não foi possível reconciliar. Para músicas e álbuns/singles, uma revisão manual foi realizada, elevando os índices de reconciliação para 94% e 98%, respectivamente.


## Outras Considerações

Após todo o trabalho, ainda restaram 11 músicas não identificadas nas fontes (2013: 1, 2007: 9, 2006: 1). Em duas delas há pelo menos a indicação dos artistas. Mesmo assim, pode haver erros no registro desses 2 casos. As músicas não identificadas são as seguintes:

|Ano|Posição|Artista|Música|
|:----|:----|:----|:----|
|2013|311|?|?|
|2007|49|?|?|
|2007|54|?|?|
|2007|97|?|?|
|2007|262|?|?|
|2007|265|?|?|
|2007|266|?|?|
|2007|267|?|?|
|2007|269|?|?|
|2007|304|Bad Company|?|
|2006|471|Alice in Chains|?|

Caso você consiga essa informação, por favor abra uma issue para que o arquivo possa ser complementado. 

Em um projeto complementar tentarei estimar quais eram as possíveis músicas, com base na análise dos dados das músicas votadas em outros anos.

---

# Análise dos dados



### Fontes

1. Planilha compilada pelo [@fabriciorby](https://x.com/fabriciorby) - https://docs.google.com/spreadsheets/d/1OHdR-RKBsELOR5nZ-L5pa8OohbvdNT29z7T-6SfWD70/
2. Blog "LISTA das 500 MAIS da KISS FM de 2000 a 2023" - https://leitespc.blogspot.com/
3. Blog "Álbuns de Cabeceira" - https://albunsdecabeceira.blogspot.com/
4. Site Whiplash - https://whiplash.net/materias/melhores/195761.html, https://whiplash.net/materias/melhores/170703.html

