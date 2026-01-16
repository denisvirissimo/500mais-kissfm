import plotly.express as px
import plotly.graph_objects as go
import bar_chart_race as bcr

def get_grafico_linha(df_data, xdata, ydata1, xlabel, ylabel, ylabel1, ydata2 = None, ylabel2 = None, reversed = False, smooth = False):
    fig = px.line()
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, separators=',.')
    fig.add_scatter(x=df_data[xdata], y=df_data[ydata1], name=ylabel1)
    if (ydata2 != None):
        fig.add_scatter(x=df_data[xdata], y=df_data[ydata2], name=ylabel2)
    fig.update_traces(hovertemplate=xlabel + ': %{x}<br> Valor: %{y}<extra></extra>')
    if (reversed):
        fig.update_layout(yaxis=dict(autorange='reversed'))
    if (smooth):
        fig.update_traces(line_shape='spline', fill='tozeroy')

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
    fig = px.bar(df_data, x=xdata, y=ydata, color=ldata, color_discrete_sequence=px.colors.qualitative.Dark24, barmode='stack')
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

def get_analise_edicao_treemap(df_data, xdata, ydata):
    path = [px.Constant('Todos')]
    path.extend(xdata)
    fig = px.treemap(df_data, path=path, values=ydata)

    fig.update_traces(marker=dict(cornerradius=5),
                    texttemplate="<b>%{label}</b><br>%{value}",
                    textposition="middle center",
                    hovertemplate=None,
                    hoverinfo="skip",
                    maxdepth=2)
    
    return fig

def gerar_grafico_race(df_data, xdata, ydata, legend, titulo):
    df_values, df_ranks = bcr.prepare_long_data(df_data, index=xdata, columns=ydata, values=legend, steps_per_period=1)
    return bcr.bar_chart_race(df_values,
                              n_bars=10,
                              steps_per_period=18,
                              period_length=1000,
                              title = titulo,
                              bar_texttemplate='{x:.0f}',
                              tick_template='{x:.0f}',
                              fixed_max=False,
                              filter_column_colors=True).data

def get_grafico_slope(df_data, xlabel, xdata1, xdata2, ydata1, ydata2, legend1, legend2, title):
    fig = go.Figure()

    for _, row in df_data.iterrows():
        fig.add_trace(go.Scatter(
            y=[row[ydata1], row[ydata2]],
            mode='lines+markers+text',
            name=f"{row[legend1]} - {row[legend2]}",
            text=[int(row[xdata1]), int(row[xdata2])],
            textposition='bottom right',
            line=dict(width=2),
            hoverinfo='none',
        ))

    fig.update_layout(yaxis=dict(autorange='reversed', title=title, showticklabels=False),
                      xaxis=dict(
                            tickvals=[0, 1],
                            ticktext=[xdata1,xdata2],
                            title=xlabel
                            ),
                      height=600,
                      legend=dict(
                        orientation="h",  
                        yanchor="bottom", 
                        y=-0.3,           
                        xanchor="center", 
                        x=0.5             
                    ))
    return fig