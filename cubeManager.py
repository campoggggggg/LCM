#cube manager: funzioni cerca, aggiungi, rimuovi, 

import sqlite3
import json
from datetime import datetime


class CubeManager:
    def __init__(self, db_path='lorcana_cards.db'):
        self.db_path = db_path #salva il percorso
        self.conn = None #connette a None
        self.cursor = None #cursor a None
    
    def connect(self): #connette al db
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row #permette di accedere alle colonne per nome
            print("✅ Connessione al database avvenuta con successo")
            return True
        except sqlite3.Error as e:
            print(f"❌ Errore di connessione al database: {e}") 
            return False
        
    def close(self): #chiude la connessione
        if self.conn:
            self.conn.close()
            print("✅ Connessione al database chiusa")

    #funzione search_cards()

    def search_cards(self, query, in_cube=False):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return []
        
        try:
            cursor = self.conn.cursor()
            search_pattern = f"%{query.lower()}%"
        
            if in_cube:
                sql = "SELECT * FROM cards WHERE LOWER(name) LIKE ? AND in_cube = 1"
            else:
                sql = "SELECT * FROM cards WHERE LOWER(name) LIKE ?"
        
            cursor.execute(sql, (search_pattern,))  # ✅ Tupla, non lista
            results = cursor.fetchall()
            print(f"✅ Trovate {len(results)} carte")
            return results
        
        except Exception as e:
            print(f"❌ Errore in search_cards: {e}")
            return []
        
    #function search_by_effect()
    def search_by_effect(self, text, in_cube=False):
        if not self.conn:
            print("❌ search_by_effect: Connessione al database non disponibile")
            return []
        
        cursor = self.conn.cursor()

        query = """
        SELECT * FROM cards 
        WHERE (body_text LIKE ? OR abilities LIKE ?)
        """
        
        if in_cube:
            query += " AND in_cube = 1"
        
        search_pattern = f"%{text}%"

        print(f"🔍 Query: {query}")  # DEBUG
        print(f"🔍 Pattern: {search_pattern}")  # DEBUG
        print(f"🔍 In cube: {in_cube}")  # DEBUG

        cursor.execute(query, (search_pattern, search_pattern))
        results = cursor.fetchall()
    
        print(f"✅ Trovate {len(results)} carte con l'effetto '{text}'")
        return results

    #funzione add_cube()
    def add_cube(self, card_id):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return False
        cursor = self.conn.cursor()
        # Controlla se la carta esiste
        cursor.execute("SELECT * FROM cards WHERE unique_id = ?", (card_id,))
        card = cursor.fetchone()
        if not card:
            print(f"❌ Carta con ID {card_id} non trovata")
            return False
        # Controlla se la carta è già nel cubo
        if card[26] == 1:  # assuming 'in_cube' is the 6th column (index 5)
            print(f"❌ Carta con ID {card_id} è già nel cubo")
            return False
        # Aggiungi la carta al cubo
        cursor.execute("UPDATE cards SET in_cube = 1 WHERE unique_id = ?", (card_id,))
        self.conn.commit()
        print(f"✅ Carta con ID {card_id} aggiunta al cubo")
        return True

    #funzione remove_cube()
    def remove_cube(self, card_id):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return False
        cursor = self.conn.cursor()
        # Controlla se la carta esiste
        cursor.execute("SELECT * FROM cards WHERE unique_id = ?", (card_id,))
        card = cursor.fetchone()
        if not card:
            print(f"❌ Carta con ID {card_id} non trovata")
            return False
        # Controlla se la carta è nel cubo
        if card[26] == 0:  # assuming 'in_cube' is the 6th column (index 5)
            print(f"❌ Carta con ID {card_id} non è nel cubo")
            return False
        # Rimuovi la carta dal cubo
        cursor.execute("UPDATE cards SET in_cube = 0 WHERE unique_id = ?", (card_id,))
        self.conn.commit()
        print(f"✅ Carta con ID {card_id} rimossa dal cubo")
        return True

    #funzione get_cube_count()
    def get_cube_count(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return 0
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cards WHERE in_cube = 1")
            result = cursor.fetchone()
            return result[0] if result else 0
        
        except Exception as e:
            print(f"❌ Errore nel conteggio delle carte nel cubo: {e}")
            return 0

       #funzione get_cube_cards()
    def get_cube_cards(self):
        if not self.conn:
            print("❌ get_cube_cardsConnessione al database non disponibile")
            return []
        cursor = self.conn.cursor()
        
        query = """
        SELECT unique_id, name, type, color, cost, Image
        FROM cards 
        WHERE in_cube = 1 
        ORDER BY name
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Converti in lista di dizionari per facilità d'uso
        cards = []
        for row in rows:
            cards.append({
                'unique_id': row[0],
                'name': row[1],
                'type': row[2],
                'color': row[3],
                'cost': row[4],
                'Image': row[5]
            })
        return cards

    #funzione get_type_count()
    def get_type_count(self, type):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return 0
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards WHERE in_cube = 1 AND LOWER(type) = LOWER(?)", (type,))
        count = cursor.fetchone()[0]
        return count

    #funzione stats_color() [Amber, Amethyst, Emerald, Ruby, Sapphire, Steel]
    def stats_color(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        total = self.get_cube_count()
        if total == 0:
            print("❌ Nessuna carta nel cubo per calcolare le statistiche")
            return {}
        cursor.execute("SELECT color, COUNT(*) AS count FROM cards WHERE in_cube = 1 GROUP BY color")
        stats = {}
        for row in cursor.fetchall():
            color = row['color'] or 'Nessuno'
            count = row['count']
            percentage = (count/total)*100
            stats[color] = {'count': count, 'percentage': percentage}
            print(f"🎨 {color:<15}: {count:>3} | {percentage:>5.2f}%")
        return stats

    #funzione stats_type() [character, action, song or location]
    def stats_type(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        total = self.get_cube_count()
        if total == 0:
            print("❌ Nessuna carta nel cubo per calcolare le statistiche")
            return {}
        cursor.execute("SELECT type, COUNT(*) AS count FROM cards WHERE in_cube = 1 GROUP BY type")
        stats = {}
        for row in cursor.fetchall():
            type = row['type'] or 'Nessuno'
            count = row['count']
            percentage = (count/total)*100
            stats[type] = {'count': count, 'percentage': percentage}
            print(f"🃏 {type:<15}: {count:>3} | {percentage:>5.2f}%")
        return stats

    #funzione cost_stats() 
    def stats_cost(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        total = self.get_cube_count()
        if total == 0:
            print("❌ Nessuna carta nel cubo per calcolare le statistiche")
            return {}
        cursor.execute("SELECT cost, COUNT(*) AS count FROM cards WHERE in_cube = 1 GROUP BY cost ORDER BY cost")
        stats = {}
        for row in cursor.fetchall():
            cost = row['cost'] or 'Nessuno'
            count = row['count']
            percentage = (count/total)*100
            stats[cost] = {'count': count, 'percentage': percentage}
            print(f"💰 {cost:<5}: {count:>3} | {percentage:5.2f}%")
        return stats

    #funzione inkable_stats()
    def stats_inkable(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        total = self.get_cube_count()
        if total == 0:
            print("❌ Nessuna carta nel cubo per calcolare le statistiche")
            return {}
        cursor.execute("""SELECT 
                    SUM(CASE WHEN inkable = 1 THEN 1 ELSE 0 END) AS inkable_yes,
                    SUM(CASE WHEN inkable = 0 THEN 1 ELSE 0 END) AS inkable_no
                    FROM cards WHERE in_cube = 1
                    """)
        row = cursor.fetchone()
        stats = {}
        inkable_yes = row['inkable_yes'] or 0
        inkable_no = row['inkable_no'] or 0
        print(f"🖋️ Inkable: {inkable_yes} | {inkable_yes/total*100:5.2f}%")
        print(f"❌ Non Inkable: {inkable_no} | {inkable_no/total*100:5.2f}%")
        stats = {
            'inkable_yes': {'count': inkable_yes, 'percentage': (inkable_yes/total)*100},
            'inkable_no': {'count': inkable_no, 'percentage': (inkable_no/total)*100}
        }
        return stats

    # funzione stats_strength()
    def stats_strength(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        tot_char = self.get_type_count('character')
        cursor.execute("""SELECT strength, COUNT(*) AS count FROM cards
                        WHERE in_cube = 1 
                    GROUP BY strength 
                    ORDER BY strength
                    """)
        stats = {}
        for row in cursor.fetchall():
            strength = row['strength'] or 'Nessuno'
            count = row['count']
            percentage = (count/tot_char)*100 
            print(f"⚔️ {strength:<5}: {count:>3} | {percentage:>5.2f}%")
            stats[strength] = {'count': count, 'percentage': percentage}
        return stats    

    #stats_willpower()
    def stats_willpower(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        tot_char = self.get_type_count('character')
        cursor.execute("""SELECT willpower, COUNT(*) AS count FROM cards
                        WHERE in_cube = 1 
                    GROUP BY willpower 
                    ORDER BY willpower
                    """)
        stats = {}
        for row in cursor.fetchall():
            willpower = row['willpower'] or 'Nessuno'
            count = row['count']
            percentage = (count/tot_char)*100
            print(f"🛡️ {willpower:<5}: {count:>3} | {percentage:>5.2f}")
            stats[willpower] = {'count': count, 'percentage': percentage}
        return stats

    #funzione lore()
    def stats_lore(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        cursor = self.conn.cursor()
        tot_char = self.get_type_count('character')

        print(f"\n🏷️  CLASSIFICAZIONI ({tot_char} Character):")

        cursor.execute("""SELECT lore, COUNT(*) AS count FROM cards
                        WHERE in_cube = 1 AND type = 'Character' OR 'Location'
                    GROUP BY lore 
                    ORDER BY lore
                    """)
        stats = {}
        for row in cursor.fetchall():
            lore = row['lore']

            if lore is None:
                continue
            
            count = row['count']
            percentage = (count/tot_char)*100
            print(f"📜 {lore:<5}: {count:>3} | {percentage:>5.2f}")
            stats[lore] = count
        return stats

    #fuznione stats_classification_character() [Hero, Villain, Ally, Floodborn, Dreamborn, etc...]

    def stats_classification(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        
        cursor = self.conn.cursor()
        tot_char = self.get_type_count('character')

        if tot_char == 0:
            print("❌ Nessun Character nel cubo per calcolare le statistiche")
            return {}
        
        cursor.execute("SELECT classifications FROM cards WHERE in_cube = 1 AND LOWER(type) = 'character'")
        
        import json
        stats = {}
        Class_list = ['Alien', 'Ally', 'Broom', 'Captain', 'Deity', 'Detective', 'Dragon', 'Dreamborn', 'Entangled',
                    'Fairy', 'Floodborn', 'Hero', 'Hyena', 'Inventor', 'King', 'Knight', 'Madrigal', 'Mentor',
                        'Musketeer', 'Pirate', 'Prince', 'Princess', 'Puppy', 'Queen', 'Racer', 'Seven Dwarfs',
                        'Song', 'Sorcerer', 'Storyborn', 'Tigger', 'Titan', 'Villain']
        
        # Inizializza contatori a zero
        for cls in Class_list:
            stats[cls] = {'count': 0}

        # Loop per contare le classificazioni
        for row in cursor.fetchall():
            try:
                classifications_str = row['classifications']

                if not classifications_str:
                    continue
                
                # ✅ CORREZIONE CRITICA: Gestisci stringa separata da virgole
                if isinstance(classifications_str, str):
                    # Le classificazioni sono salvate come "Storyborn, Ally" non come JSON
                    class_list = [c.strip().strip('"').strip("'") for c in classifications_str.split(',')]
                elif isinstance(classifications_str, list):
                    # Se è già una lista, usala direttamente
                    class_list = classifications_str
                else:
                    continue

                # ✅ DEBUG: Stampa per vedere cosa contiene
                #print(f"🔍 DEBUG - class_list type: {type(class_list)}, content: {class_list}")

                # Ora itera sulla lista (non sulle lettere!)
                for classification in class_list:
                    # Pulisci da spazi, virgolette singole e doppie
                    classification = str(classification).strip().strip('"').strip("'")
                    
                    # ✅ DEBUG: Stampa ogni classificazione processata
                    #print(f"🔍 Processing: '{classification}'")
                    
                    if classification in Class_list:
                        stats[classification]['count'] += 1
                        #print(f"✅ Trovata in lista: {classification}, count ora: {stats[classification]['count']}")
                    else:
                        if classification:  # Solo se non è vuoto
                            if classification not in stats:
                                stats[classification] = {'count': 1}
                            else:
                                stats[classification]['count'] += 1
                            print(f"⚠️ Nuova classificazione: {classification}")
            
            except Exception as e:
                print(f"❌ Errore nel parsing delle classificazioni: {e}")
                pass
        
        # Rimuovi classificazioni con count = 0
        stats = {k: v for k, v in stats.items() if v['count'] > 0}

        if not stats:
            print("❌ Nessuna classificazione trovata nel cubo")
            return {}

        # Calcola percentuali e stampa
        for classification in sorted(stats.keys(), key=lambda x: stats[x]['count'], reverse=True):
            count = stats[classification]['count']
            percentage = (count/tot_char)*100
            stats[classification]['percentage'] = percentage
            bar = "█" * int(percentage / 3)

            print(f"🔖 {classification:<15}: {count:>3} | {percentage:>5.2f}% {bar}")
        
        return stats




    #funzione stats_keyword() [Challenger, Evasive, Rush, etc...]
    def stats_keyword(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        
        cursor = self.conn.cursor()
        tot_char = self.get_type_count('character')

        if tot_char == 0:
            print("❌ Nessun Character nel cubo")
            return {}

        print(f"\n🔑 PAROLE CHIAVE ({tot_char} Character):")

        keywords = [
                'Challenger', 'Evasive', 'Rush', 'Ward', 'Shift', 
                'Bodyguard', 'Reckless', 'Singer', 'Support', 'Resist'
        ]
        
        stats = {}

        # ✅ CORREZIONE: Loop per contare le keyword
        for keyword in keywords:
            cursor.execute("""SELECT COUNT(*) AS count FROM cards
                            WHERE in_cube = 1 AND LOWER(type) = 'character' 
                            AND LOWER(Abilities) LIKE ?
                        """, (f"%{keyword.lower()}%",))
            
            count = cursor.fetchone()['count']
            if count > 0:
                percentage = (count/tot_char)*100
                stats[keyword] = {'count': count, 'percentage': percentage}

        # ✅ CORREZIONE: Questo loop deve essere FUORI dal loop precedente
        for keyword in sorted(stats.keys(), key=lambda x: stats[x]['count'], reverse=True):
            count = stats[keyword]['count']
            percentage = stats[keyword]['percentage']
            bar = "█" * int(percentage / 3)
            print(f"🔑 {keyword:<15}: {count:>3} | {percentage:>5.2f}% {bar}")

        if not stats:
            print("❌ Nessuna parola chiave trovata nel cubo")
            
        return stats
            
    #funzione stats_text_quotes() [cerca specifiche parole nell'effetto delle carte]
    def stats_text_quotes(self, words):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        
        search_text = input("🔍 Inserisci le parole da cercare: ")

        if not search_text.strip():
            print("❌ Nessuna parola inserita")
            return {}
        
        cursor = self.conn.cursor()

        cursor.execute("""SELECT COUNT(*) AS count FROM cards
                        WHERE in_cube = 1 
                        AND LOWER(body_text) LIKE ?
                    """, (f"%{search_text.lower()}%",))
        results = cursor.fetchall()
        if results:
            print(f"\n📜 Carte trovate: {len(results)}")

            for i, card in enumerate(results, 1):
                print(f"{i}. {card['name']}")
                print(f"   {card['type']} | {card['color']} | Costo: {card['cost']}")
                
                body = card['body_text'] or "Nessun testo"

                if len(body) > 100:
                    body = body[:100] + "..."
                print(f"   Testo: {body}\n")
                print()
        else:
            print("❌ Nessuna carta trovata con quel testo")
        return results

    #funzione stats_all() [esegue tutte le statistiche]
    def stats_all(self):
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return {}
        total = self.get_cube_count()
        if total == 0:
            print("❌ Nessuna carta nel cubo per calcolare le statistiche")
            return {}  

        print("\n" + "=" * 30 + " ANALISI CUBO " + "=" * 30)
        self.stats_color()
        self.stats_type()
        self.stats_cost()
        self.stats_inkable()
        self.strength()
        self.willpower()
        self.lore()
        self.stats_classification()
        self.stats_keyword()
        print("=" * 70 + "\n")

    #menù interattivo per scegliere quale funzione eseguire
    def menu(self):
        while True:
            print("\n" + "=" * 30 + " GESTIONE CUBO " + "=" * 30)
            print("\n1.  🎨 Distribuzione per colore")
            print("2.  🃏 Distribuzione per tipo")
            print("3.  💎 Distribuzione per costo")
            print("4.  ⚔️ Distribuzione per forza")
            print("5.  🛡️ Distribuzione per volontà")
            print("6.  🏷️ Classificazioni")
            print("7.  🔑 Keywords")
            print("8.  📝 Cerca nel testo")
            print("9.  🖋️ Inkable/Non-Inkable")
            print("10. 📊 TUTTE LE STATISTICHE")
            print("0.  ← Indietro")
            choice = input("Scegli un'opzione (1-10) o 0: ")
            
            if choice == '1':
                self.stats_color()
            elif choice == '2':
                self.stats_type()
            elif choice == '3':
                self.stats_cost()
            elif choice == '4':
                self.strength()
            elif choice == '5':
                self.willpower()
            elif choice == '6':
                self.stats_classification()
            elif choice == '7':
                self.stats_keyword()
            elif choice == '8':
                self.stats_text_quotes()
            elif choice == '9':
                self.stats_inkable()
            elif choice == '10':
                self.stats_all()
            elif choice == '0':
                break
            else:
                print("❌ Scelta non valida. Riprova.")

    def setup_tournaments_table(self):
        """Crea le tabelle per tracciare i tornei"""
        if not self.conn:
            return False
        
        cursor = self.conn.cursor()
        
        # Tabella tornei
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournaments (
                tournament_id INTEGER PRIMARY KEY AUTOINCREMENT,
                winner_name TEXT NOT NULL,
                colors TEXT NOT NULL,
                tournament_date DATE NOT NULL,
                notes TEXT
            )
        ''')
        
        # Tabella mazzi vincitori (molti-a-molti con cards)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournament_decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER NOT NULL,
                card_unique_id TEXT NOT NULL,
                FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id),
                FOREIGN KEY (card_unique_id) REFERENCES cards(unique_id)
            )
        ''')
        
        self.conn.commit()
        print("✅ Tabelle tornei create")
        return True

    def add_tournament(self, winner_name, colors, date, deck_cards):
        """Registra un nuovo torneo"""
        if not self.conn:
            return False
        
        cursor = self.conn.cursor()
        
        try:
            # Inserisci torneo
            cursor.execute(
                "INSERT INTO tournaments (winner_name, colors, tournament_date) VALUES (?, ?, ?)",
                (winner_name, colors, date)
            )
            tournament_id = cursor.lastrowid
            
            # Inserisci carte del mazzo
            for card_id in deck_cards:
                cursor.execute(
                    "INSERT INTO tournament_decks (tournament_id, card_unique_id) VALUES (?, ?)",
                    (tournament_id, card_id)
                )
            
            self.conn.commit()
            print(f"✅ Torneo registrato: {winner_name} - {colors}")
            return True
        
        except Exception as e:
            print(f"❌ Errore registrazione torneo: {e}")
            self.conn.rollback()
            return False

    def get_all_tournaments(self):
        """Recupera tutti i tornei"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tournament_id, winner_name, colors, tournament_date 
            FROM tournaments 
            ORDER BY tournament_date DESC
        """)
        
        return cursor.fetchall()

    def get_tournament_deck(self, tournament_id):
        """Recupera il mazzo di un torneo specifico"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.unique_id, c.name, c.type, c.color, c.cost, c.Image
            FROM cards c
            JOIN tournament_decks td ON c.unique_id = td.card_unique_id
            WHERE td.tournament_id = ?
        """, (tournament_id,))
        
        return cursor.fetchall()

    def get_card_winrate(self):
        """Statistiche carte con più vittorie"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                c.name,
                c.type,
                c.color,
                COUNT(td.tournament_id) as wins
            FROM cards c
            JOIN tournament_decks td ON c.unique_id = td.card_unique_id
            GROUP BY c.unique_id
            ORDER BY wins DESC
            LIMIT 50
        """)
        
        return cursor.fetchall()

    def get_color_winrate(self):
        """Statistiche colori con più vittorie"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                colors,
                COUNT(*) as wins
            FROM tournaments
            GROUP BY colors
            ORDER BY wins DESC
        """)
        
        return cursor.fetchall()

    def get_winner_stats(self):
        """Statistiche vincitori"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                winner_name,
                COUNT(*) as wins,
                GROUP_CONCAT(DISTINCT colors) as colors_used
            FROM tournaments
            GROUP BY winner_name
            ORDER BY wins DESC
        """)
        
        return cursor.fetchall()

    def export_cube_to_json(self, filename=None):
        """Esporta il cubo corrente in un file JSON"""
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return False
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cube_backup_{timestamp}.json"
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT unique_id FROM cards WHERE in_cube = 1")
            cards_in_cube = [row[0] for row in cursor.fetchall()]
            
            backup_data = {
                "export_date": datetime.now().isoformat(),
                "total_cards": len(cards_in_cube),
                "card_ids": cards_in_cube
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Cubo esportato in {filename} ({len(cards_in_cube)} carte)")
            return filename
        
        except Exception as e:
            print(f"❌ Errore export: {e}")
            return False

    def import_cube_from_json(self, filename, clear_existing=False):
        """Importa un cubo da file JSON"""
        if not self.conn:
            print("❌ Connessione al database non disponibile")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            card_ids = backup_data.get('card_ids', [])
            
            if not card_ids:
                print("❌ Nessuna carta nel backup")
                return False
            
            cursor = self.conn.cursor()
            
            # Opzionale: pulisci il cubo esistente
            if clear_existing:
                cursor.execute("UPDATE cards SET in_cube = 0")
                print("🗑️ Cubo esistente pulito")
            
            # Importa le carte
            success_count = 0
            not_found = []
            
            for card_id in card_ids:
                cursor.execute("SELECT unique_id FROM cards WHERE unique_id = ?", (card_id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE cards SET in_cube = 1 WHERE unique_id = ?", (card_id,))
                    success_count += 1
                else:
                    not_found.append(card_id)
            
            self.conn.commit()
            
            print(f"✅ Importate {success_count}/{len(card_ids)} carte")
            
            if not_found:
                print(f"⚠️ {len(not_found)} carte non trovate nel database:")
                for card_id in not_found[:10]:  # Mostra solo le prime 10
                    print(f"  - {card_id}")
            
            return True
        
        except Exception as e:
            print(f"❌ Errore import: {e}")
            return False

    def get_cube_id_list(self):
        """Ritorna la lista semplice di ID delle carte nel cubo"""
        if not self.conn:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT unique_id FROM cards WHERE in_cube = 1 ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
