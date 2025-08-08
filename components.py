import streamlit as st
import streamlit.components.v1 as components

css_file = './resources/style.css'

@st.cache_data
def load_css():
    with open(css_file) as f:
        return f'<style>{f.read()}</style>'

def top10(df_data):
    html = load_css()
    html+="""

      <div class="list">
          <div class="list__body">
            <table class="list__table">
              <tbody>
    """

    for index, row in df_data.iterrows():
        html += '<tr class="list__row"><td class="list__cell"><span class="list__value">' + str(row.Posicao_Atual) +'</span></td>'
        html += '<td class="list__cell"><span class="list__value">'+row.Musica+'</span><small class="list__label"></small></td>'
        html += '<td class="list__cell"><span class="list__value">'+row.Artista+'</span><small class="list__label"></small>'
        if (row.Variacao > 0):
            html += '</td><td class="list__cell list__icon__green">▲ ' + str(row.Variacao) + '</td></tr>'
        elif (row.Variacao < 0):
            html += '</td><td class="list__cell list__icon__red">▼ ' + str(row.Variacao * -1) + '</td></tr>'
        else:
            html += '</td><td class="list__cell list__icon__grey">■ 0</td></tr>'

    html+="""
            </tbody></table>
          </div>
        </div>

    """
    return components.html(html, height=600, width=550)