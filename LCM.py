#cubo lorcana app su streamlit

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cubeManager import CubeManager

#conf. pagina
st.set_page_config(page_title="Lorcana Cube Manager",
                   page_icon="🧊",
                   layout="wide", 
                   initial_sidebar_state="expanded"
)
st.title("🧊 Lorcana Cube Manager")

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
@st.cache_resource
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
    "Scelect a section:",
    ["🏠 Dashboard", "🔍 Search cards", "➕ Cube management", "📊 Distribution", "📜 Rules"]
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
        col1, col2, col3, col4 = st.columns(4)
        
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
        <p style='color: black; font-size: 14px; margin: 0;'>🖋️ Inkable</p>
        <p style='font-size: 32px; font-weight: 600; margin: 0;'>
            {inkable_count} <span style='font-size: 20px; color: gray;'>({inkable_perc:.1f}%)</span>
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
        <p style='color: black; font-size: 14px; margin: 0;'>❌🖋️ Uninkable</p>
        <p style='font-size: 32px; font-weight: 600; margin: 0;'>
            {uninkable_count} <span style='font-size: 20px; color: gray;'>({uninkable_perc:.1f}%)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
                
            else:
                st.metric("❌🖋️ Uninkable", "0 (0.0%)")

        with col4:
            st.markdown(f"Best ink triplets wr: ToDo")
        st.markdown("---")
        
        # Grafici principali in colonne
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 Inks distribution")
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
            st.subheader("🃏 Type distribution")
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
        st.subheader("⚜️ Current cube gallery")

        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            cards_per_row = st.selectbox(
                "Cards per row:",
                [4, 6, 8],
                index=2
            )

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
    if cube_cards:
        # Applica filtro colore se selezionato
        if filter_color != "All":
            cube_cards = [card for card in cube_cards if filter_color.lower() in str(card['color']).lower()]
        
        # Ordina le carte
        if sort_by == "Name":
            cube_cards.sort(key=lambda x: x['name'])
        elif sort_by == "Cost":
            cube_cards.sort(key=lambda x: (x['cost'] if x['cost'] is not None else 999, x['name']))
        elif sort_by == "Color":
            cube_cards.sort(key=lambda x: (x['color'], x['name']))
        elif sort_by == "Type":
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

    else:
        st.warning("No cards in cube yet!")

# ============================================================================
# PAGINA: CERCA CARTE
# ============================================================================
elif page == "🔍 Search cards":
    st.header("🔍 by name")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search",
            placeholder="Es: Elsa, Mickey, Maleficent...",
            label_visibility="collapsed",)
    
    with col2:
        in_cube_only = st.checkbox("Only cards actually in cube", value=False)
    
    if search_query:
        results = manager.search_cards(search_query, in_cube=in_cube_only)
        
        if results:
            st.success(f"✅ Found {len(results)} cards")
            
            # Converti in DataFrame per visualizzazione
            columns = ['id', 'name', 'type', 'color', 'cost', 'inkable', 'strength', 
                      'willpower', 'lore', 'rarity', 'in_cube']
            
            df = pd.DataFrame(results, columns=range(len(results[0])))
            
            # Seleziona solo le colonne che ci interessano (adatta gli indici)
            display_df = pd.DataFrame({
                'ID': df[0],
                'Name': df[1],
                'Type': df[6],
                'Ink': df[7],
                'Classification': df[16],
                'Keyword(s)': df[19],
                'Cost': df[8],
                'Inkable': df[9].apply(lambda x: '✅' if x == 1 else '❌'),
                'Strength': df[10],
                'Willpower': df[11],
                'Lore': df[12],
                'In cube?': df[26].apply(lambda x: '✅' if x == 1 else '❌')
            })
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download CSV
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Scarica risultati (CSV)",
                csv,
                "ricerca_carte.csv",
                "text/csv"
            )
        else:
            st.warning("❌ No cards found")

    if cube_count == 0:
        st.warning("⚠️ Cube is empty!")
    else:
        st.subheader("🔍 by card effect")

        col1, col2 = st.columns([3, 1])
        with col1:
            search_text = st.text_input("Search",
            placeholder="Es: Deal 1 damage, Draw 1 card, etc...",
            label_visibility="collapsed",
            key = "search_effect")
        
        with col2:
            in_cube_only_effect = st.checkbox("Only cards actually in cube", value=False, key='in_cube_effect')

        if search_text:
            results = manager.search_by_effect(search_text, in_cube=in_cube_only_effect)
            
            if results:
                st.success(f"✅ Found {len(results)} cards")
                
                #Converti in DataFrame per visualizzazione
                df = pd.DataFrame(results, columns=range(len(results[0])))
            
                # Seleziona solo le colonne che ci interessano
                display_df = pd.DataFrame({
                    'ID': df[0],
                    'Name': df[1],
                    'Type': df[6],
                    'Ink': df[7],
                    'Cost': df[8],
                    'Effect': df[17].apply(lambda x: x[:100] + '...' if x and len(str(x)) > 100 else x),  # Tronca testo lungo
                    'In cube?': df[26].apply(lambda x: '✅' if x == 1 else '❌')
                })
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download CSV
                csv = display_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Scarica risultati effetti (CSV)",
                    csv,
                    "ricerca_effetti.csv",
                    "text/csv",
                    key="download_effects"
                )

            else:
                st.warning("❌ No cards found")
        st.markdown("---")
        
        
# ============================================================================
# PAGINA: GESTIONE CUBO
# ============================================================================
elif page == "➕ Cube management":
    st.header("➕ Cube management")
    
    tab1, tab2 = st.tabs(["➕ Add cards", "➖ Remove cards"])
    
    with tab1:
        st.subheader("Add cards to cube")
        
        search_add = st.text_input("🔎 Cerca carta da aggiungere:", 
                                   key="add_search")
        
        if search_add:
            results = manager.search_cards(search_add, in_cube=False)
            
            if results:
                for idx, card in enumerate(results):
                    bg_color = "#f0f0f0" if idx % 2 == 0 else "transparent"
                    st.markdown(f"<div style='background-color: {bg_color}; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{card[1]}** - {card[6]} | {card[7]} | Costo: {card[8]}")
                    
                    with col2:
                        if card[26] == 1:
                            st.success("✅ In cube")
                        else:
                            st.info("⚪ Not in cube")
                    
                    with col3:
                        if card[26] == 0:
                            if st.button("➕ Add", key=f"add_{card[0]}"):
                                if manager.add_cube(card[0]):
                                    st.success(f"✅ {card[1]} Done!")
                                    st.rerun()
                                else:
                                    st.error("❌ Error")
                    st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Remove cards from cube")
        
        search_remove = st.text_input("🔎 Cerca carta da rimuovere:", 
            key="remove_search")
        
        if search_remove:
            results = manager.search_cards(search_remove, in_cube=True)
            
            if results:
                for card in results:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"**{card[1]}** - {card[6]} | {card[7]} | Costo: {card[8]}")
                    
                    with col2:
                        if st.button("➖ Remove", key=f"remove_{card[0]}"):
                            if manager.remove_cube(card[0]):
                                st.success(f"✅ {card[1]} Done!")
                                st.rerun()
                            else:
                                st.error("❌ Error")
            else:
                st.info("No cards found in cube")

    st.markdown("---")
    st.markdown("##")  # Spazio extra
    st.markdown("---")

    st.subheader("📊 Report")
    if st.button("🚀 Generate a complete Report", type="primary"):
        with st.spinner("Loading"):
            # Tabs per organizzare tutte le stats
            tabs = st.tabs(["🎨 Inks", "🃏 Type", "💎 Cost", "🏷️ Classification", "🔑 Keywords"])
            
            with tabs[0]:
                stats = manager.stats_color()
                if stats:
                    df = stats_to_df(stats)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    fig = px.pie(df, values='Count', names='Name')
                    st.plotly_chart(fig, use_container_width=True)
            
            with tabs[1]:
                stats = manager.stats_type()
                if stats:
                    df = stats_to_df(stats)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            
            with tabs[2]:
                stats = manager.stats_cost()
                if stats:
                    df = stats_to_df(stats)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            
            with tabs[3]:
                stats = manager.stats_classification()
                if stats:
                    df = stats_to_df(stats)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            
            with tabs[4]:
                stats = manager.stats_keyword()
                if stats:
                    df = stats_to_df(stats)
                    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# PAGINA: STATISTICHE
# ============================================================================
elif page == "📊 Distribution":
    st.header("📊 Cube distributions")
    
    if cube_count == 0:
        st.warning("⚠️ Cube is empty!")
    else:
        stat_choice = st.selectbox(
            "Choose 1 statistics to analyze:",
            ["🎨 Inks", "🃏 Type", "💎 Cost", "🖋️ Inkable", 
             "⚔️ Strength", "🛡️ Willpower", "📜 Lore", "🏷️ Classification", "🔑 Keywords"]
        )
        
        if stat_choice == "🎨 Inks":
            stats = manager.stats_color()
            if stats:
                df = stats_to_df(stats)

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
                
                df['Nome'] = df['Nome'].apply(classify_color)
                df = df.groupby('Nome', as_index=False).sum()

                df['Sort_Order'] = df['Nome'].apply(lambda x: 1 if x == 'Multicolor' else 0)
                df = df.sort_values(['Sort_Order', 'Nome']).drop('Sort_Order', axis=1)

                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True)
                with col2:
                    fig = px.bar(df, x='Nome', y='Conteggio', color='Nome',
                                text='Percentuale', color_discrete_map=lorcana_colors,
                                labels={'Nome': 'Ink',
                                        'Conteggio': '#',
                                        'Percentuale': '%'})
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "🃏 Type":
            stats = manager.stats_type()
            if stats:
                df = stats_to_df(stats)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True)
                with col2:
                    fig = px.pie(df, values='Conteggio', names='Nome',
                                 labels={'Nome': 'Type', 'Conteggio': '#'})
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "💎 Cost":
            stats = manager.stats_cost()
            if stats:
                df = stats_to_df(stats)
                df = df.sort_values('Nome') 
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['Nome'],
                    y=df['Conteggio'],
                    mode='lines+markers',
                    fill='tozeroy',
                    line=dict(color='royalblue', width=3),
                    marker=dict(size=10)
                ))
                fig.update_layout(
                    title="Mana curve",
                    xaxis_title="Cost",
                    yaxis_title="Number of cards",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True)
        
        elif stat_choice == "🖋️ Inkable":
            stats = manager.stats_inkable()
            if stats:
                df = stats_to_df(stats)
                df['Nome'] = df['Nome'].replace({'inkable_yes': 'Inkable', 'inkable_no': 'Non-Inkable'})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(df, hide_index=True)
                with col2:
                    fig = px.pie(df, values='Conteggio', names='Nome',
                                color_discrete_map={'Inkable': 'lightblue', 'Non-Inkable': 'lightcoral'})
                    st.plotly_chart(fig, use_container_width=True)
        
        elif stat_choice == "⚔️ Strength":
            stats = manager.stats_strength()
            if stats:
                df = stats_to_df(stats)
                st.bar_chart(df.set_index('Nome')['Conteggio'])
                st.dataframe(df, hide_index=True)
        
        elif stat_choice == "🛡️ Willpower":
            stats = manager.stats_willpower()
            if stats:
                df = stats_to_df(stats)
                st.bar_chart(df.set_index('Nome')['Conteggio'])
                st.dataframe(df, hide_index=True)
        
        elif stat_choice == "📜 Lore":
            stats = manager.stats_lore()
            if stats:
                df = stats_to_df(stats)
                st.bar_chart(df.set_index('Nome')['Conteggio'])
                st.dataframe(df, hide_index=True)
        
        elif stat_choice == "🏷️ Classification":
            stats = manager.stats_classification()
            if stats:
                df = stats_to_df(stats)
                df = df.sort_values('Conteggio', ascending=False)
                
                fig = px.bar(df.head(15), x='Conteggio', y='Nome', 
                            orientation='h', text='Conteggio')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True)
        
        elif stat_choice == "🔑 Keywords":
            stats = manager.stats_keyword()
            if stats:
                df = stats_to_df(stats)
                df = df.sort_values('Conteggio', ascending=False)
                
                fig = px.bar(df, x='Nome', y='Conteggio', color='Conteggio',
                            color_continuous_scale='Viridis', text='Conteggio',
                            labels={'Nome': 'Keyword', 'Conteggio': '#'})
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df, hide_index=True)

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
    - Visualize distributions with pie charts and bar graphs.

    #### 2. Search Cards by Name
    - Search for specific cards by entering their name.
    - Option to filter results to show only cards currently in your cube.
    - Download search results as a CSV file.

    #### 3. Cube Management
    - Add cards to your cube by searching for them and clicking the "Add" button.
    - Remove cards from your cube by searching for them and clicking the "Remove" button.
    - Generate a comprehensive report of your cube's statistics including inks, types, costs, classifications, and keywords.

    #### 4. Distribution
    - Analyze various statistics of your cube such as inks, types, costs, inkable status, strength, willpower, lore, classifications, and keywords.
    - Visualize data with interactive charts.



    Enjoy managing your Lorcana card cube!
    """)
    
    
# Footer
st.sidebar.markdown("---")
st.sidebar.info("Lorcana Cube Manager v1.0\nCreated by camposssssss")