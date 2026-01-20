import plotly.express as px
import plotly.graph_objects as go
import bar_chart_race as bcr

def get_grafico_linha(df_data, xdata, ydata, xlabel, ylabels, show_text = False, reversed = False, smooth = False, percentage = False):
    fig = px.line()
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabels[0], separators=',.')
    fig.add_scatter(x=df_data[xdata], y=df_data[ydata[0]], name=ylabels[1])
    fig.update_traces(hovertemplate=xlabel + ': %{x}<br>' + ylabels[1] + ': %{y}<extra></extra>')

    if (len(ydata) > 1):
        fig.add_scatter(x=df_data[xdata], y=df_data[ydata[1]], name=ylabels[2], hovertemplate=xlabel + ': %{x}<br>' + ylabels[2] + ': %{y}<extra></extra>')

    if(show_text):
        fig.update_traces(textposition='top center', mode='lines+text', text=df_data[ydata[0]])
    if (reversed):
        fig.update_layout(yaxis=dict(autorange='reversed'))
    if (smooth):
        fig.update_traces(line_shape='spline', fill='tozeroy')
    if (percentage):
        fig.update_layout(yaxis_tickformat='.1%')
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

    if x_diagonal:
        fig.update_xaxes(tickangle=-45)

    return fig

def get_grafico_barra_stacked(df_data, xdata, ydata, ldata, xlabel, ylabel, legend):
    fig = px.bar(df_data, x=xdata, y=ydata, color=ldata, color_discrete_sequence=px.colors.qualitative.Dark24, barmode='stack')
    fig.update_layout(xaxis_type='category', xaxis_title = xlabel, yaxis_title=ylabel, legend_title=legend, legend_traceorder="reversed")
    fig.update_traces(hovertemplate='%{fullData.name}<br>' + xlabel + ": %{label}<br>" + ylabel + ": %{value}<extra></extra>")
    fig.update_xaxes(categoryorder='array', categoryarray=df_data.sort_values(xdata)[xdata].to_list())

    return fig

def get_grafico_pizza(df_data, values, names, value_label, name_label):
    fig = px.pie(df_data, values=values, names=names)
    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate=name_label + ": %{label}<br>" + value_label + ": %{value}<br>" + 'Percentual' + ": %{percent}<br>")
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

def gerar_grafico_race(df_data, xdata, ydata, legend, title):
    df_values, df_ranks = bcr.prepare_long_data(df_data, index=xdata, columns=ydata, values=legend, steps_per_period=1)
    return bcr.bar_chart_race(df_values,
                              n_bars=10,
                              steps_per_period=18,
                              period_length=1000,
                              title = title,
                              bar_texttemplate='{x:.0f}',
                              tick_template='{x:.0f}',
                              fixed_max=False,
                              filter_column_colors=True).data

def get_grafico_slope(df_data, xlabel, xdata, ydata, legends, title):
    fig = go.Figure()

    for _, row in df_data.iterrows():
        fig.add_trace(go.Scatter(
            y=[row[ydata[0]], row[ydata[1]]],
            mode='lines+markers+text',
            name=f"{row[legends[0]]} - {row[legends[1]]}",
            text=[int(row[xdata[0]]), int(row[xdata[1]])],
            textposition='bottom right',
            line=dict(width=2),
            hoverinfo='none',
        ))

    fig.update_layout(yaxis=dict(autorange='reversed', title=title, showticklabels=False),
                      xaxis=dict(
                            tickvals=[0, 1],
                            ticktext=[xdata[0],xdata[1]],
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

def adicionar_linha_tendencia(fig, df_data, trend_data, xdata, ydata, ylabel):
    return fig.add_scatter(x=df_data[xdata], y=trend_data(df_data[ydata]), name=ylabel, line_dash='dash', hovertemplate='<extra></extra>', mode='lines')