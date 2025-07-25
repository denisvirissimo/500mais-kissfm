import plotly.express as px
import plotly.graph_objects as go
import bar_chart_race as bcr

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
    if (df_data.select_dtypes(include='datetime').columns.size > 0):
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

def get_mapa(df_data, locations, color, hover_name, title):
    fig = px.choropleth(df_data,
                        locationmode="country names",
                        locations=locations,
                        color=color,
                        hover_name=hover_name,
                        color_continuous_scale = px.colors.sequential.YlOrRd, projection='natural earth')

    fig.update_layout(coloraxis_colorbar=dict(title=title))

    return fig

def get_mapa_calor(df_data, xhover, yhover, zhover, xlabel, ylabel):
    fig = go.Figure(data=go.Heatmap(
                        z=df_data,
                        x=df_data.columns,
                        y=df_data.index,
                        text=df_data,
                        colorscale='viridis',
                        reversescale=True,
                        name="",
                        hovertemplate= xhover + ': %{x}<br>' + yhover + ': %{y}<br>' + zhover + ': %{z}',
                        texttemplate="%{text}"))

    fig.update_layout(xaxis_type='category',
                  xaxis_title = xlabel,
                  yaxis_title = ylabel,
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