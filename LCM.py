#cubo lorcana app su streamlit

import streamlit as st
import re
import streamlit.components.v1 as components
import json 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cubeManager import CubeManager
from datetime import datetime

#conf. pagina
st.set_page_config(page_title="Lorcana Cube Manager",
                   page_icon="🏰",
                   layout="wide", 
                   initial_sidebar_state="expanded"
)
st.title("🏰 Lorcana Cube Manager")

# CSS personalizzato
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #2b2b47;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione sessione
#@st.cache_resource
def init_manager():
    import os
    
    # Debug: verifica se il database esiste
    if not os.path.exists('lorcana_cards.db'):
        st.error("❌ File lorcana_cards.db non trovato!")
        st.info("💡 Esegui 'python main.py' per creare il database")
        return None
    
    manager = CubeManager()
    
    # Debug: stampa il risultato della connessione
    connection_result = manager.connect()
    #st.write(f"🔍 DEBUG - Connessione riuscita: {connection_result}")
    #st.write(f"🔍 DEBUG - manager.conn: {manager.conn}")
    
    if connection_result:
        #print(f"✅ Manager cached - conn: {manager.conn}")
        return manager
    else:
        #st.error("❌ Impossibile connettersi al database")
        return None
    
# Inizializza il manager
manager = init_manager()
cards_per_row = 8  # Default cards per row

# AGGIUNGI QUESTO CONTROLLO
if manager is None:
    st.error("❌ ERRORE CRITICO: Impossibile inizializzare il database")
    st.stop()  # Ferma l'esecuzione dell'app

# Ora è sicuro usare manager
cube_count = manager.get_cube_count()

# Funzione per convertire stats in DataFrame
def stats_to_df(stats):
    if not stats:
        return pd.DataFrame()
    data = []
    for key, value in stats.items():
        if isinstance(value, dict):
            data.append({
                'Nome': key,
                'Conteggio': value.get('count', 0),
                'Percentuale': value.get('percentage', 0)
            })
        else:
            data.append({
                'Nome': key,
                'Conteggio': value,
                'Percentuale': 0
            })
    return pd.DataFrame(data)

# HEADER
#st.markdown('<h1 class="main-header">🎴 Lorcana Cube Manager</h1>', unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("📋 Menu")
page = st.sidebar.radio(
    "Select a section:",
    ["🏠 Dashboard", "➕ Cube management", "📊 Other stats", "🏆 Report a tournament", "📈 Tournament stats", "💾 Backup/Restore", "📜 Rules"]
)

# Mostra conteggio cubo sempre visibile
cube_count = manager.get_cube_count()
st.sidebar.markdown("---")
st.sidebar.metric("🎴 total cards in cube", cube_count)

# ============================================================================
# PAGINA: DASHBOARD
# ============================================================================
if page == "🏠 Dashboard":
    st.header("📊 Cube overview")
    
    if cube_count == 0:
        st.warning("⚠️ Cube is empty! Add some cards to see stats.")
    else:
        # Metriche principali
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎴 Total cards", cube_count)
        
        # Calcola stats rapide
        type_stats = manager.stats_type()
        total_card = manager.get_cube_count()
        inkable_stats = manager.stats_inkable()
        
        
        with col2:
            if inkable_stats:
                inkable_count = inkable_stats.get('inkable_yes', {}).get('count', 0)
                inkable_perc = inkable_stats.get('inkable_yes', {}).get('percentage', 0)
    
                st.markdown(f"""
    <div style='text-align: left;'>
        <p style='color: ; font-size: 14px; margin: 0;'>🖋️ Inkable</p>
        <p style='font-size: 32px; font-weight: 600; margin: 0;'>
            {inkable_count} <span style='font-size: 20px; color: gray;'>{inkable_perc:.1f}%</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
                
            else:
                st.metric("🖋️ Inkable", "0 (0.0%)")

        with col3:
            if inkable_stats:
                uninkable_count = total_card - inkable_stats.get('inkable_yes', {}).get('count', 0)
                uninkable_perc = 100 - inkable_stats.get('inkable_yes', {}).get('percentage', 0)
    
                st.markdown(f"""
    <div style='text-align: left;'>
        <p style='color: ; font-size: 14px; margin: 0;'>❌🖋️ Uninkable</p>
        <p style='font-size: 32px; font-weight: 600; margin: 0;'>
            {uninkable_count} <span style='font-size: 20px; color: gray;'>{uninkable_perc:.1f}%</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
                
            else:
                st.metric("❌🖋️ Uninkable", "0 (0.0%)")
        
        # Grafici principali in colonne
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 Total inks")
            color_stats = manager.stats_color()
            if color_stats:
                df_colors = stats_to_df(color_stats)
                # ✅ Mappa dei colori Lorcana
                lorcana_colors = {
                    'Amber': '#f0b101',      # Giallo/Ambra
                    'Amethyst': '#7f387a',   # Viola
                    'Emerald': '#288933',    # Verde
                    'Ruby': '#d00731',       # Rosso
                    'Sapphire': '#0087bf',   # Blu
                    'Steel': '#9da7b1',      # Grigio
                    'Multicolor': '#2a2a47'  # Nero/Grigio scuro per dual color
                }
                
                def classify_color(nome):
                    nome_str = str(nome) if nome else 'Unknown'
                    if '/' in nome_str or ',' in nome_str:
                        return 'Multicolor'
                    return nome_str
        
                df_colors['Nome'] = df_colors['Nome'].apply(classify_color)
                df_colors = df_colors.groupby('Nome', as_index=False).sum()

                df_colors['Sort_Order'] = df_colors['Nome'].apply(lambda x: 1 if x == 'Multicolor' else 0)
                df_colors = df_colors.sort_values(['Sort_Order', 'Nome']).drop('Sort_Order', axis=1)
        
        # Crea la lista dei colori in base ai dati
                color_map = {}
                for nome in df_colors['Nome']:  # ✅ Usa 'Nome' non 'Name'
                    nome_str = str(nome) if nome else 'Nessuno'
                
                    # Controlla se è multicolor
                    if '/' in nome_str or ',' in nome_str:
                        color_map[nome_str] = '#2C3E50'
                    else:
                        color_map[nome_str] = lorcana_colors.get(nome_str, '#808080')
                fig = px.pie(
                    df_colors, 
                    values='Conteggio', 
                    names='Nome',
                    color='Nome',
                    color_discrete_map=lorcana_colors  # ✅ Usa la mappa personalizzata
                )
        
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=12,
                    pull=[0.05]*len(df_colors)
                )
                
                fig.update_layout(
                    height=350,  # Altezza fissa
                    margin=dict(l=10, r=10, t=32, b=10),  # Margini
                    showlegend=True
                )

                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🃏 Total types")
            if type_stats:
                df_types = stats_to_df(type_stats)
                fig = px.bar(df_types, x='Nome', y='Conteggio', 
                            color='Nome', text='Conteggio')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
        
        # Curva di mana
        st.subheader("💎 Mana curve")
        cost_stats = manager.stats_cost()
        if cost_stats:
            df_cost = stats_to_df(cost_stats)
            df_cost = df_cost.sort_values('Nome')
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_cost['Nome'],
                y=df_cost['Conteggio'],
                marker_color='lightblue',
                text=df_cost['Conteggio'],
                textposition='outside'
            ))
            fig.update_layout(
                xaxis_title="Costo di Mana",
                yaxis_title="Numero di Carte",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        #Galleria cubo attuale
        st.markdown("---")
        st.subheader("⚜️ Cube gallery")

        col_filter2, col_filter3 = st.columns(2)

        with col_filter2:
            sort_by = st.selectbox(
                "Sort by:",
                ["name", "cost", "color", "type",],
                index=0
            )

        with col_filter3:
            filter_color = st.selectbox(
                "Filter by ink:",
                ["All", "Amber", "Amethyst", "Emerald", "Ruby", "Sapphire", "Steel", "Multicolor"],
            )

        cube_cards = manager.get_cube_cards()

    cube_cards = manager.get_cube_cards() if manager else []
    
    # Applica filtro colore se selezionato
    if filter_color != "All":
        cube_cards = [card for card in cube_cards if filter_color.lower() in str(card['color']).lower()]
        
    # Ordina le carte
    if sort_by == "name":
        cube_cards.sort(key=lambda x: x['name'])
    elif sort_by == "cost":
        cube_cards.sort(key=lambda x: (x['cost'] if x['cost'] is not None else 999, x['name']))
    elif sort_by == "color":
        cube_cards.sort(key=lambda x: (x['color'], x['name']))
    elif sort_by == "type":
        cube_cards.sort(key=lambda x: (x['type'], x['name']))
    
        # CSS per le card
    st.markdown("""
        <style>
            .card-container {
                position: relative;
                border-radius: 10px;
                overflow: hidden;
                transition: transform 0.2s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                margin-bottom: 15px;
            }
            .card-container:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(255,107,107,0.5);
                z-index: 10;
            }
            .card-img {
                width: 100%;
                height: auto;
                display: block;
                border-radius: 10px;
            }
            .card-name {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 5px;
                font-size: 0.8em;
                text-align: center;
                opacity: 0;
                transition: opacity 0.2s;
            }
            .card-container:hover .card-name {
                opacity: 1;
            }
            /* Riduci il gap tra le colonne */
            [data-testid="column"] {
                padding: 0 5px !important;
            }
            </style>
    """, unsafe_allow_html=True)
        
    # Crea la griglia
    cols = st.columns(cards_per_row, gap="small")
    
    for idx, card in enumerate(cube_cards):
        col_idx = idx % cards_per_row
        
        with cols[col_idx]:
            Image = card['Image'] if card['Image'] else f"https://via.placeholder.com/300x420?text={card['name']}"
            
            # Mostra la carta
            st.markdown(f"""
                <div class="card-container">
                    <img src="{Image}" class="card-img" alt="{card['name']}">
                    <div class="card-name">{card['name']}</div>
                </div>
            """, unsafe_allow_html=True)
# ============================================================================
# PAGINA: GESTIONE CUBO
# ============================================================================









elif page == "➕ Cube management":
    st.header("Add or remove cards from your cube")
    
    # =======================
    # FILTRI (sempre visibili in alto)
    # =======================
    with st.container():
        st.subheader("🔎 Filter cards")

        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
        with col1:
            filter_name = st.text_input("Search by name, ID, effect or keyword...", 
                                       value="", 
                                       key="filter_name_input",
                                       placeholder="Type name, effect or ID",
                                       label_visibility="collapsed")
        with col2:
            all_colors = ["Amber", "Amethyst", "Emerald", "Ruby", "Sapphire", "Steel"]
            selected_colors = st.multiselect("Choose 1 or more ink(s)", 
                                            all_colors, 
                                            key="filter_colors",
                                            placeholder="Select inks...",
                                            label_visibility="collapsed")
        with col3:
            all_types = ["Character", "Action", "Action - Song", "Item", "Location"]
            selected_types = st.multiselect("Choose 1 or more type(s)", 
                                           all_types, 
                                           key="filter_types",
                                           placeholder="Select types...",
                                           label_visibility="collapsed")
        with col4:
            inkable_filter = st.selectbox("Inkable status",
                                         ["All cards", "Inkable only", "Uninkable only"],
                                         key="inkable_filter",
                                         label_visibility="collapsed")
        with col5:
            cube_filter = st.selectbox("Cube status",
                                      ["All cards", "In cube only", "Not in cube"],
                                      key="cube_filter",
                                      label_visibility="collapsed")

    # =======================
    # ✅ CARICA SOLO SE NECESSARIO (con cache)
    # =======================
    @st.cache_data(ttl=10)  # Cache per 10 secondi
    def load_filtered_cards(name_filter, color_filter, type_filter, ink_status, cube_status):
        """Carica e filtra le carte - con cache per velocizzare"""
        all_rows = manager.search_cards("")
        all_cards = []

        for r in all_rows:
            row = dict(r)
            
            in_cube_value = row.get("in_cube")
            # Converti None a 0, altrimenti usa il valore
            in_cube_normalized = 1 if in_cube_value == 1 else 0
            
            all_cards.append({
                "unique_id": row.get("unique_id") or "",
                "name": row.get("name") or "",
                "image": row.get("Image") or "",
                "color": row.get("color") or "",
                "type": row.get("type") or "",
                "cost": row.get("cost") or "",
                "in_cube": in_cube_normalized,
                "inkable": row.get("inkable", 0),
                "body_text": str(row.get("body_text") or ""),
                "classifications": str(row.get("classifications") or ""),
            })

        # Applica filtri
        filtered = all_cards

        # Filtro per stato cubo
        if cube_status == "In cube only":
            filtered = [c for c in filtered if c['in_cube'] == 1]
        elif cube_status == "Not in cube":
            filtered = [c for c in filtered if c['in_cube'] == 0]
        # Se "All cards", non filtra nulla

        # Filtro inkable o no
        if ink_status == "Inkable only":
            filtered = [c for c in filtered if c['inkable'] == 1]
        elif ink_status == "Uninkable only":
            filtered = [c for c in filtered if c['inkable'] == 0]
        # Se "All", non filtra nulla

        # Filtro per nome, ID, effetto o classificazione
        if name_filter and name_filter.strip():
            term = name_filter.lower()
            
            def matches_search(card):
                name_match = term in (card.get('name') or "").lower()
                id_match = term in (card.get('unique_id') or "").lower()
                effect_match = term in (card.get('body_text') or "").lower()
                class_match = term in (card.get('classifications') or "").lower()
                return name_match or id_match or effect_match or class_match
            
            filtered = [c for c in filtered if matches_search(c)]

        if color_filter:
            sel = [s.lower() for s in color_filter]

            def card_has_color(card):
                raw = card.get('color') or ""
                parts = [p.strip().lower() for p in re.split(r'[,/]', raw) if p.strip()]
                return any(s in parts for s in sel)

            filtered = [c for c in filtered if card_has_color(c)]

        if type_filter:
            sel_types = [t.lower() for t in type_filter]
            filtered = [c for c in filtered if (c.get('type') or "").lower() in sel_types]

        return filtered

    # Carica carte filtrate
    filtered_cards = load_filtered_cards(filter_name, tuple(selected_colors), tuple(selected_types), inkable_filter, cube_filter)
    
    total_cards = len(filtered_cards)
    
    st.markdown("---")
    st.write(f"**Found {total_cards} cards**")

    # =======================
    # PAGINAZIONE (48 carte fisse per pagina)
    # =======================
    if total_cards == 0:
        st.warning("No cards found with these filters")
    else:
        cards_per_page = 48  # Fisso a 48 carte per pagina
        
        # Inizializza pagina corrente in session_state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0

        total_pages = (total_cards - 1) // cards_per_page + 1
        
        # Controlli paginazione
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page = 0
                st.rerun()
        
        with col2:
            if st.button("◀️ Prev", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col3:
            st.markdown(f"<h4 style='text-align: center;'>Page {st.session_state.current_page + 1} / {total_pages}</h4>", 
                       unsafe_allow_html=True)
        
        with col4:
            if st.button("Next ▶️", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1
                st.rerun()
        
        with col5:
            if st.button("Last ⏭️", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page = total_pages - 1
                st.rerun()

        # =======================
        # MOSTRA SOLO LA PAGINA CORRENTE
        # =======================
        start_idx = st.session_state.current_page * cards_per_page
        end_idx = min(start_idx + cards_per_page, total_cards)
        current_page_cards = filtered_cards[start_idx:end_idx]

        # CSS personalizzato
        st.markdown("""
            <style>
            .card-image {
                width: 100%;
                border-radius: 8px;
                transition: transform 0.2s;
                display: block;
                position: relative;
            }
            .card-image:hover {
                transform: scale(1.05);
            }
            div[data-testid="column"] {
                padding: 2px !important;
            }
            /* Nascondi il margine dell'elemento markdown */
            div[data-testid="stMarkdownContainer"] {
                margin-bottom: 0 !important;
            }
            /* Stile per il bottone "In Cube" (verde e disabilitato) */
            button[kind="primary"]:disabled {
                background-color: #228B22 !important;
                color: white !important;
                opacity: 1 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Griglia - solo carte della pagina corrente
        cards_per_row = 8
        
        for i in range(0, len(current_page_cards), cards_per_row):
            cols = st.columns(cards_per_row, gap="small")
            
            for idx, card in enumerate(current_page_cards[i:i+cards_per_row]):
                with cols[idx]:
                    img = card['image'] or f"https://via.placeholder.com/300x420?text={card['name']}"
                    in_cube = card['in_cube'] == 1
                    
                    # Mostra solo l'immagine
                    st.markdown(f'<img src="{img}" class="card-image" alt="{card["name"]}">', 
                               unsafe_allow_html=True)
                    
                    # Bottoni Add/Remove
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        # Usa un bottone disabilitato invece di success
                        if in_cube:
                            st.button("✓", key=f"incube_{card['unique_id']}", 
                                     disabled=True, use_container_width=True, 
                                     type="primary")
                        else:
                            if st.button("➕", key=f"add_{card['unique_id']}", use_container_width=True):
                                if manager.add_cube(card['unique_id']):
                                    st.cache_data.clear()
                                    st.rerun()
                    
                    with col_btn2:
                        if st.button("➖", key=f"rem_{card['unique_id']}", use_container_width=True):
                            if manager.remove_cube(card['unique_id']):
                                st.cache_data.clear()
                                st.rerun()
        
        # Ripeti controlli paginazione in basso
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⏮️ First", key="first_bottom", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page = 0
                st.rerun()
        
        with col2:
            if st.button("◀️ Prev", key="prev_bottom", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col3:
            if st.button("▶️ Next", key="next_bottom", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1
                st.rerun()
        
        with col4:
            if st.button("⏭️ Last", key="last_bottom", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page = total_pages - 1
                st.rerun()













# ============================================================================
# PAGINA: STATISTICHE
# ============================================================================












elif page == "📊 Other stats":
    st.header("📊 Choose one statistic")
    
    if cube_count == 0:
        st.warning("⚠️ Cube is empty!")
    else:
        stat_choice = st.selectbox(
            "Choose one statistic to analyze:",
            ["🎨 Inks", "🃏 Type", "💎 Cost", "🖋️ Inkable", 
             "⚔️ Strength", "🛡️ Willpower", "📜 Lore", "🏷️ Classification", "🔑 Keywords"]
        )
        
        if stat_choice == "🎨 Inks":
            stats = manager.stats_color()
            if stats:
                df = stats_to_df(stats)
                # Rinomina colonne
                df = df.rename(columns={'Nome': 'Ink', 'Conteggio': 'Cards', 'Percentuale': '%'})

                lorcana_colors = {
                    'Amber': '#f0b101',
                    'Amethyst': '#7f387a',
                    'Emerald': '#288933',
                    'Ruby': '#d00731',
                    'Sapphire': '#0087bf',
                    'Steel': '#9da7b1',
                    'Multicolor': '#2a2a47'
                }

                def classify_color(name):
                    nome_str = str(name) if name else 'Nessuno'
                    if '/' in nome_str or ',' in nome_str:
                        return 'Multicolor'
                    return nome_str
                
                df['Ink'] = df['Ink'].apply(classify_color)
                df = df.groupby('Ink', as_index=False).sum()

                df['Sort_Order'] = df['Ink'].apply(lambda x: 1 if x == 'Multicolor' else 0)
                df = df.sort_values(['Sort_Order', 'Ink']).drop('Sort_Order', axis=1)

                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True, use_container_width=True)
                with col2:
                    fig = px.bar(df, x='Ink', y='Cards', color='Ink',
                                text='%', color_discrete_map=lorcana_colors)
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(
                        title="Ink Distribution",
                        showlegend=False,
                        xaxis_title="Ink Color",
                        yaxis_title="Number of Cards"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "🃏 Type":
            stats = manager.stats_type()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Card Type', 'Conteggio': 'Cards', 'Percentuale': '%'})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True, use_container_width=True)
                with col2:
                    fig = px.pie(df, values='Cards', names='Card Type',
                                title="Card Type Distribution")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "💎 Cost":
            stats = manager.stats_cost()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Mana Cost', 'Conteggio': 'Cards', 'Percentuale': '%'})
                df = df.sort_values('Mana Cost')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Mana Cost'],
                    y=df['Cards'],
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='royalblue', width=3),
                    marker=dict(size=10),
                    text=df['%'].apply(lambda x: f"{x:.1f}%"),
                    textposition='top center'
                ))
                fig.update_layout(
                    title="Mana Curve",
                    xaxis_title="Mana Cost",
                    yaxis_title="Number of Cards",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
        
        elif stat_choice == "🖋️ Inkable":
            stats = manager.stats_inkable()
            if stats:
                df = stats_to_df(stats)
                df['Nome'] = df['Nome'].replace({'inkable_yes': 'Inkable', 'inkable_no': 'Non-Inkable'})
                df = df.rename(columns={'Nome': 'Status', 'Conteggio': 'Cards', 'Percentuale': '%'})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True, use_container_width=True)
                with col2:
                    fig = px.pie(df, values='Cards', names='Status',
                                title="Inkable vs Non-Inkable",
                                color_discrete_map={'Inkable': 'lightblue', 'Non-Inkable': 'lightcoral'})
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "⚔️ Strength":
            stats = manager.stats_strength()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Strength', 'Conteggio': 'Cards', 'Percentuale': '%'})
                
                fig = px.bar(df, x='Strength', y='Cards', 
                            title="Strength Distribution",
                            text='Cards',
                            color='Cards',
                            color_continuous_scale='Reds')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_title="Strength Value", yaxis_title="Number of Cards")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
        
        elif stat_choice == "🛡️ Willpower":
            stats = manager.stats_willpower()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Willpower', 'Conteggio': 'Cards', 'Percentuale': '%'})
                
                fig = px.bar(df, x='Willpower', y='Cards',
                            title="Willpower Distribution", 
                            text='Cards',
                            color='Cards',
                            color_continuous_scale='Blues')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_title="Willpower Value", yaxis_title="Number of Cards")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
        
        elif stat_choice == "📜 Lore":
            stats = manager.stats_lore()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Lore', 'Conteggio': 'Cards', 'Percentuale': '%'})
                
                fig = px.bar(df, x='Lore', y='Cards',
                            title="Lore Distribution",
                            text='Cards',
                            color='Cards',
                            color_continuous_scale='Purples')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_title="Lore Value", yaxis_title="Number of Cards")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
        
        elif stat_choice == "🏷️ Classification":
            stats = manager.stats_classification()
            
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Classification', 'Conteggio': 'Cards', 'Percentuale': '%'})
                df = df.sort_values('Cards', ascending=False)
                
                fig = px.bar(df.head(15), x='Cards', y='Classification', 
                            orientation='h', 
                            title="Top 15 Classifications",
                            text='Cards',
                            color='Cards',
                            color_continuous_scale='Viridis')
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    height=600,
                    xaxis_title="Number of Cards",
                    yaxis_title="Classification"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
        
        elif stat_choice == "🔑 Keywords":
            stats = manager.stats_keyword()
            if stats:
                df = stats_to_df(stats)
                df = df.rename(columns={'Nome': 'Keyword', 'Conteggio': 'Cards', 'Percentuale': '%'})
                df = df.sort_values('Cards', ascending=False)
                
                fig = px.bar(df, x='Keyword', y='Cards', 
                            title="Keyword Distribution",
                            text='Cards',
                            color='Cards',
                            color_continuous_scale='Viridis')
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_title="Keyword", yaxis_title="Number of Cards")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ No keywords found in cube")
















# =======================
# PAGINA: REPORT A TOURNAMENT
# =======================

elif page == "🏆 Report a tournament":
    st.header("🏆 Report a tournament")
    
    # Setup tabella tornei se non esiste
    manager.setup_tournaments_table()
    
    # Form per inserire dati torneo
    st.subheader("📝 Tournament information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        winner_name = st.text_input("Winner name", placeholder="Es: Giuseppe Trippa")
        tournament_date = st.date_input("Tournament date")
    
    with col2:
        all_colors = ["Amber", "Amethyst", "Emerald", "Ruby", "Sapphire", "Steel"]
        selected_colors = st.multiselect(
            "Ink triplet (select 1-3 colors)", 
            all_colors, 
            max_selections=3,
            key="tournament_colors"
        )
        
        # Mostra colori selezionati
        if selected_colors:
            colors_str = " / ".join(selected_colors)
            st.info(f"🎨 Selected: **{colors_str}**")
    
    st.markdown("---")
    
    # Controlla che ci siano i dati minimi
    if not winner_name or not selected_colors:
        st.warning("Enter winner name and winning inks")
    else:
        st.subheader(f"🃏 Build {winner_name}'s deck")
        
        # Inizializza session state per il mazzo
        if 'tournament_deck' not in st.session_state:
            st.session_state.tournament_deck = []

        #Hidden inkaster toggle
        if 'include_hidden_inkcaster' not in st.session_state:
            st.session_state.include_hidden_inkcaster = False
        
        st.markdown("#### 🎴 Did you play Hidden Inkcaster in your deck?")
        col_toggle, col_info = st.columns([1, 3])

        with col_toggle:
            include_inkcaster = st.checkbox(
                "Add Hidden Inkcaster",
                value=st.session_state.include_hidden_inkcaster,
                key="inkcaster_checkbox"
            )
            st.session_state.include_hidden_inkcaster = include_inkcaster
        
        with col_info:
            if include_inkcaster:
                st.success("✅ Hidden Inkcaster will be added to the deck (doesn't count toward 40 cards)")
            else:
                st.info("ℹ️ Hidden Inkcaster can be added to any deck regardless of ink colors")
        
        st.markdown("---")
        
        # Calcola conteggio carte (Hidden Inkcaster non conta se incluso)
        HIDDEN_INKCASTER_ID = "URS-098"
        
        # Rimuovi Hidden Inkcaster dal conteggio se presente
        deck_cards_without_inkcaster = [
            card_id for card_id in st.session_state.tournament_deck 
            if card_id != HIDDEN_INKCASTER_ID
        ]
        
        # Mostra conteggio carte nel mazzo
        deck_count = len(st.session_state.tournament_deck)

        # Aggiungi/Rimuovi automaticamente Hidden Inkcaster
        if include_inkcaster and HIDDEN_INKCASTER_ID not in st.session_state.tournament_deck:
            st.session_state.tournament_deck.insert(0, HIDDEN_INKCASTER_ID)
        elif not include_inkcaster and HIDDEN_INKCASTER_ID in st.session_state.tournament_deck:
            st.session_state.tournament_deck.remove(HIDDEN_INKCASTER_ID)
        
        
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("📦 Cards in deck", deck_count)
        with col_info2:
            if deck_count >= 40:
                st.success("✅ Deck complete (40+)")
            else:
                st.warning(f"⚠️ Need {40 - deck_count} more cards")
        with col_info3:
            if st.button("🗑️ Clear deck", type="secondary"):
                st.session_state.tournament_deck = []
                st.rerun()
        
        # Carica carte del cubo con i colori selezionati
        @st.cache_data(ttl=10)
        def load_cube_cards_filtered(colors_tuple):
            """Carica carte del cubo filtrate per colori"""
            all_rows = manager.search_cards("", in_cube=True)
            filtered_cards = []
            
            colors_lower = [c.lower() for c in colors_tuple]
            
            for r in all_rows:
                row = dict(r)
                card_colors = str(row.get("color") or "").lower()
                
                # Controlla se la carta ha SOLO i colori selezionati
                card_color_list = [c.strip() for c in card_colors.replace('/', ',').split(',')]
                
                # La carta deve avere solo colori della tripla selezionata
                if all(cc in colors_lower for cc in card_color_list if cc):
                    filtered_cards.append({
                        "unique_id": row.get("unique_id") or "",
                        "name": row.get("name") or "",
                        "image": row.get("Image") or "",
                        "color": row.get("color") or "",
                        "type": row.get("type") or "",
                        "cost": row.get("cost") or "",
                    })
            
            return filtered_cards
        
        available_cards = load_cube_cards_filtered(tuple(selected_colors))
        
        st.write(f"**Available cards: {len(available_cards)}**")
        
        # Paginazione
        cards_per_page = 48
        
        if 'tournament_page' not in st.session_state:
            st.session_state.tournament_page = 0
        
        total_pages = (len(available_cards) - 1) // cards_per_page + 1 if available_cards else 0
        
        if total_pages > 0:
            # Controlli paginazione
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️", key="first_t", disabled=(st.session_state.tournament_page == 0)):
                    st.session_state.tournament_page = 0
                    st.rerun()
            
            with col2:
                if st.button("◀️", key="prev_t", disabled=(st.session_state.tournament_page == 0)):
                    st.session_state.tournament_page -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f"<h4 style='text-align: center;'>Page {st.session_state.tournament_page + 1} / {total_pages}</h4>", 
                           unsafe_allow_html=True)
            
            with col4:
                if st.button("▶️", key="next_t", disabled=(st.session_state.tournament_page >= total_pages - 1)):
                    st.session_state.tournament_page += 1
                    st.rerun()
            
            with col5:
                if st.button("⏭️", key="last_t", disabled=(st.session_state.tournament_page >= total_pages - 1)):
                    st.session_state.tournament_page = total_pages - 1
                    st.rerun()
            
            # Mostra carte della pagina corrente
            start_idx = st.session_state.tournament_page * cards_per_page
            end_idx = min(start_idx + cards_per_page, len(available_cards))
            current_cards = available_cards[start_idx:end_idx]
            
            # CSS
            st.markdown("""
                <style>
                .card-image {
                    width: 100%;
                    border-radius: 8px;
                    transition: transform 0.2s;
                    display: block;
                }
                .card-image:hover {
                    transform: scale(1.05);
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Griglia carte
            cards_per_row = 8
            
            for i in range(0, len(current_cards), cards_per_row):
                cols = st.columns(cards_per_row, gap="small")
                
                for idx, card in enumerate(current_cards[i:i+cards_per_row]):
                    with cols[idx]:
                        img = card['image'] or f"https://via.placeholder.com/300x420?text={card['name']}"
                        
                        st.markdown(f'<img src="{img}" class="card-image" alt="{card["name"]}">', 
                                   unsafe_allow_html=True)
                        
                        # Controlla se già nel mazzo
                        in_deck = card['unique_id'] in st.session_state.tournament_deck
                        
                        if in_deck:
                            # Mostra quante copie
                            count = st.session_state.tournament_deck.count(card['unique_id'])
                            if st.button(f"✓ ({count})", key=f"td_{card['unique_id']}_{idx}", 
                                       disabled=True, type="primary", use_container_width=True):
                                pass
                        else:
                            if st.button("➕", key=f"tadd_{card['unique_id']}_{idx}", use_container_width=True):
                                st.session_state.tournament_deck.append(card['unique_id'])
                                st.rerun()
        
        # Bottone salva torneo
        st.markdown("---")
        
        if deck_count >= 40:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Save Tournament", type="primary", use_container_width=True):
                    colors_str = "/".join(selected_colors)
                    success = manager.add_tournament(
                        winner_name, 
                        colors_str, 
                        tournament_date.isoformat(),
                        st.session_state.tournament_deck
                    )
                    
                    if success:
                        st.success(f"🎉 Tournament saved! Winner: {winner_name}")
                        st.session_state.tournament_deck = []
                        st.session_state.tournament_page = 0
                        st.balloons()
                    else:
                        st.error("❌ Error saving tournament")
        else:
            st.info("ℹ️ Add at least 40 cards to save the tournament")















# =======================
# PAGINA: TOURNAMENT STATS
# =======================

elif page == "📈 Tournament stats":
    st.header("📈 Tournament Statistics")
    
    # Verifica se ci sono tornei
    all_tournaments = manager.get_all_tournaments()
    
    if not all_tournaments:
        st.warning("⚠️ No tournaments registered yet!")
        st.info("Go to 🏆 Report a tournament to add your first tournament")
    else:
        st.success(f"📊 Total tournaments: **{len(all_tournaments)}**")
        
        # Tabs per diverse statistiche
        tab1, tab2, tab3, tab4 = st.tabs([
            "🃏 Top Cards", 
            "🎨 Color Combos", 
            "👑 Top Players",
            "📜 Tournament History"
        ])
        
        # =======================
        # TAB 1: TOP CARDS
        # =======================
        with tab1:
            st.subheader("🃏 Most winning cards")
            
            card_stats = manager.get_card_winrate()
            
            if card_stats:
                # Converti in DataFrame
                df_cards = pd.DataFrame(card_stats, columns=['Card Name', 'Type', 'Color', 'Wins'])
                
                # Top 20
                top_20 = df_cards.head(20)
                
                # Grafico
                fig = px.bar(
                    top_20, 
                    x='Wins', 
                    y='Card Name',
                    orientation='h',
                    color='Wins',
                    color_continuous_scale='Viridis',
                    title="Top 20 Cards by Tournament Wins",
                    text='Wins'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    height=800,
                    xaxis_title="Tournament Wins",
                    yaxis_title="Card Name",
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabella completa
                st.markdown("### 📋 Complete list")
                st.dataframe(df_cards, use_container_width=True, hide_index=True)
                
                # Download CSV
                csv = df_cards.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "top_cards.csv",
                    "text/csv"
                )
            else:
                st.info("No card statistics available yet")
        
        # =======================
        # TAB 2: COLOR COMBOS
        # =======================
        with tab2:
            st.subheader("🎨 Most winning color combinations")
            
            color_stats = manager.get_color_winrate()
            
            if color_stats:
                df_colors = pd.DataFrame(color_stats, columns=['Color Combo', 'Wins'])
                
                # Calcola percentuali
                total_tournaments = len(all_tournaments)
                df_colors['Win Rate %'] = (df_colors['Wins'] / total_tournaments * 100).round(2)
                
                # Grafico a torta
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        df_colors,
                        values='Wins',
                        names='Color Combo',
                        title="Color Combo Distribution"
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Grafico a barre
                    fig = px.bar(
                        df_colors,
                        x='Color Combo',
                        y='Wins',
                        text='Wins',
                        color='Wins',
                        color_continuous_scale='Rainbow',
                        title="Wins by Color Combo"
                    )
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tabella
                st.dataframe(df_colors, use_container_width=True, hide_index=True)
            else:
                st.info("No color statistics available yet")
        
        # =======================
        # TAB 3: TOP PLAYERS
        # =======================
        with tab3:
            st.subheader("👑 Top players")
            
            winner_stats = manager.get_winner_stats()
            
            if winner_stats:
                df_winners = pd.DataFrame(winner_stats, columns=['Player', 'Wins', 'Colors Used'])
                
                # Podio
                st.markdown("### 🏆 Podium")
                
                if len(df_winners) >= 3:
                    col1, col2, col3 = st.columns(3)
                    
                    with col2:
                        st.markdown("### 🥇")
                        st.metric("1st Place", df_winners.iloc[0]['Player'], 
                                 f"{df_winners.iloc[0]['Wins']} wins")
                    
                    with col1:
                        st.markdown("### 🥈")
                        st.metric("2nd Place", df_winners.iloc[1]['Player'], 
                                 f"{df_winners.iloc[1]['Wins']} wins")
                    
                    with col3:
                        st.markdown("### 🥉")
                        st.metric("3rd Place", df_winners.iloc[2]['Player'], 
                                 f"{df_winners.iloc[2]['Wins']} wins")
                
                st.markdown("---")
                
                # Grafico
                fig = px.bar(
                    df_winners,
                    x='Player',
                    y='Wins',
                    text='Wins',
                    color='Wins',
                    color_continuous_scale='Blues',
                    title="Wins by Player"
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(xaxis_title="Player", yaxis_title="Tournament Wins")
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabella completa
                st.dataframe(df_winners, use_container_width=True, hide_index=True)
            else:
                st.info("No player statistics available yet")
        
        # =======================
        # TAB 4: TOURNAMENT HISTORY
        # =======================
        with tab4:
            st.subheader("📜 Tournament history")
            
            # Mostra tutti i tornei
            df_tournaments = pd.DataFrame(
                all_tournaments, 
                columns=['ID', 'Winner', 'Colors', 'Date']
            )
            
            st.dataframe(df_tournaments, use_container_width=True, hide_index=True)
            
            # Visualizza dettaglio torneo
            st.markdown("---")
            st.subheader("🔍 View tournament details")
            
            tournament_ids = [t[0] for t in all_tournaments]
            tournament_labels = [f"{t[1]} - {t[2]} ({t[3]})" for t in all_tournaments]
            
            selected_tournament = st.selectbox(
                "Select tournament",
                range(len(tournament_ids)),
                format_func=lambda x: tournament_labels[x]
            )
            
            if selected_tournament is not None:
                tournament_id = tournament_ids[selected_tournament]
                deck_cards = manager.get_tournament_deck(tournament_id)
                
                st.write(f"**Deck size:** {len(deck_cards)} cards")
                
                # Mostra il mazzo
                deck_df = pd.DataFrame(
                    deck_cards,
                    columns=['ID', 'Name', 'Type', 'Color', 'Cost', 'Image']
                )
                
                # Statistiche del mazzo
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    type_counts = deck_df['Type'].value_counts()
                    st.write("**Types:**")
                    for t, c in type_counts.items():
                        st.write(f"- {t}: {c}")
                
                with col2:
                    avg_cost = deck_df['Cost'].mean()
                    st.metric("Average Cost", f"{avg_cost:.2f}")
                
                with col3:
                    color_counts = deck_df['Color'].value_counts()
                    st.write("**Color distribution:**")
                    for c, count in color_counts.items():
                        st.write(f"- {c}: {count}")
                
                # Tabella carte
                st.dataframe(
                    deck_df[['Name', 'Type', 'Color', 'Cost']], 
                    use_container_width=True, 
                    hide_index=True
                )














elif page == "💾 Backup/Restore":
    st.header("💾 Backup & Restore Cube")
    
    cube_count = manager.get_cube_count()
    
    st.info(f"📦 Current cube: **{cube_count} cards**")
    
    # =======================
    # EXPORT
    # =======================
    st.subheader("📤 Export Cube")
    st.write("Save your current cube to a JSON file")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        export_filename = st.text_input(
            "Backup filename",
            value=f"cube_backup_{datetime.now().strftime('%Y%m%d')}.json"
        )
    
    with col2:
        st.write("")  # spacer
        st.write("")
        if st.button("📥 Export Cube", type="primary", use_container_width=True):
            if cube_count == 0:
                st.warning("⚠️ Cube is empty!")
            else:
                result = manager.export_cube_to_json(export_filename)
                if result:
                    st.success(f"✅ Cube exported to `{result}`")
                    
                    # Offri download
                    with open(result, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    
                    st.download_button(
                        label="⬇️ Download Backup File",
                        data=backup_content,
                        file_name=result,
                        mime="application/json"
                    )
                else:
                    st.error("❌ Export failed")
    
    # Mostra lista ID (per debug/controllo)
    with st.expander("🔍 View card IDs in cube"):
        card_ids = manager.get_cube_id_list()
        st.code("\n".join(card_ids), language="text")
        
        # Download lista semplice
        ids_text = "\n".join(card_ids)
        st.download_button(
            "📄 Download ID list (txt)",
            ids_text,
            f"cube_ids_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain"
        )
    
    st.markdown("---")
    
    # =======================
    # IMPORT
    # =======================
    st.subheader("📥 Import Cube")
    st.write("Restore a cube from a backup file")
    
    uploaded_file = st.file_uploader(
        "Choose backup file (JSON)",
        type=['json'],
        help="Upload a cube backup file created with Export"
    )
    
    if uploaded_file:
        # Leggi il file
        backup_data = json.load(uploaded_file)
        
        st.success(f"✅ File loaded: {backup_data.get('total_cards', 0)} cards")
        st.info(f"📅 Backup date: {backup_data.get('export_date', 'Unknown')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            clear_cube = st.checkbox(
                "🗑️ Clear existing cube before import",
                value=True,
                help="Remove all cards from cube before importing"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("📤 Import Cube", type="primary", use_container_width=True):
                # Salva temporaneamente il file
                temp_filename = "temp_backup.json"
                with open(temp_filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f)
                
                # Importa
                success = manager.import_cube_from_json(temp_filename, clear_existing=clear_cube)
                
                if success:
                    st.success("✅ Cube imported successfully!")
                    st.balloons()
                    # Pulisci cache
                    st.cache_data.clear()
                    
                    # Rimuovi file temporaneo
                    import os
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    
                    st.rerun()
                else:
                    st.error("❌ Import failed")
    
    st.markdown("---")
    st.warning("⚠️ **Important**: Always keep backups of your cube!")















# ============================================================================
# PAGINA: REGOLE
# ============================================================================
elif page == "📜 Rules":
    st.header("📜 Rules")
    st.markdown("""
    ### Cube: How to play!
    - Each player receives 3 15-card booster packs

    - Players simultaneously choose one card from their booster, and pass the remaining cards face-down to the player to their left (1st and 3rd pack) or right (2nd and 4th pack).

    - Repeat until there's no cards left in the first packs.
                
    - Everyone builds a deck with the 60 cards they just drafted, plus a copy of "Hidden Inkcaster" (prior given to each player).
                
    - Each deck must have at least 40 cards, and can be played with up to 3 different inks.
                
    - Choose tournament structure.
                
    - Play with the deck you just built!
                

    


    ### Lorcana Cube Manager - User Guide

    Welcome to the Lorcana Cube Manager! This application helps you manage your custom Lorcana card cube. Below are the main features and how to use them:

    #### 1. Dashboard
    - View an overview of your cube including total cards, types, inks, and inkable cards.
    - Visualize statistics with pie charts and bar graphs.

    #### 2. Cube Management
    - Add cards to your cube by searching for them and clicking the "Add" button.
    - Remove cards from your cube by searching for them and clicking the "Remove" button.

    #### 3. Report
    - Analyze various statistics of your cube such as inks, types, costs, inkable status, strength, willpower, lore, classifications, and keywords.
    - Visualize data with interactive charts.



    Enjoy and happy cubing! 
                

    """)
    
    
# Footer
st.sidebar.markdown("---")
st.sidebar.info("Lorcana Cube Manager v1.0\nCreated by camposssssss")
st.markdown("---")
st.sidebar.info("'No no no no no no kid. Giving up is for rookies - 🎬 Hercules'")