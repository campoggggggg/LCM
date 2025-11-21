import pandas as pd
import sqlite3
import json
import os

print("\n" + "="*70)
print("📂 CARICAMENTO DATABASE DA JSON LOCALE")
print("="*70)

# Verifica che card.json esista
if not os.path.exists("card.json"):
    print("❌ Errore: card.json non trovato!")
    print("💡 Scaricalo manualmente da: https://api.lorcana-api.com/bulk/cards")
    print("   e salvalo come 'card.json' nella stessa cartella")
    exit(1)
# Carica dati dal JSON locale
print("\n📂 Caricamento dati da card.json...")
with open("card.json", "r", encoding="utf-8") as f:
    data = json.load(f)


print(f"✅ Caricati {len(data)} carte dal JSON locale")

# Converti in DataFrame
df = pd.json_normalize(data)
print(f"✅ Dati caricati in DataFrame con {len(df)} carte")
df.columns = df.columns.str.lower()

# Connetti al database SQLite
print("\n📥 Connessione al database SQLite...")
conn = sqlite3.connect('lorcana_cards.db')
cursor = conn.cursor()

# Crea tabella
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        unique_id TEXT PRIMARY KEY,
        name TEXT,
        card_num INTEGER,
        set_name TEXT,
        set_num INTEGER,
        set_id TEXT,
        type TEXT,
        color TEXT,
        cost INTEGER,
        inkable INTEGER,
        strength INTEGER,
        willpower INTEGER,
        lore INTEGER,
        move_cost INTEGER,
        rarity TEXT,
        franchise TEXT,
        classifications TEXT,
        body_text TEXT,
        flavor_text TEXT,
        abilities TEXT,
        artist TEXT,
        Image TEXT,
        gamemode TEXT,
        date_added TEXT,
        date_modified TEXT,
        card_variants TEXT,
        in_cube INTEGER DEFAULT 0
    )
''')
conn.commit()
print("✅ Tabella 'cards' creata o già esistente")

# Inserisci dati nel database
print("\n📥 Inserimento dati nel database...")

for _, row in df.iterrows():
    cursor.execute('''
        INSERT OR REPLACE INTO cards (
            unique_id, name, card_num, set_name, set_num, set_id, type, color, cost,
            inkable, strength, willpower, lore, move_cost, rarity, franchise,
            classifications, body_text, flavor_text, abilities, artist, Image,
            gamemode, date_added, date_modified, card_variants, in_cube
        ) VALUES (?,
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
    ''', (
        row.get('unique_id'),
        row.get('name'),
        row.get('card_num'),
        row.get('set.name'),
        row.get('set.set_num'),
        row.get('set.set_id'),
        row.get('type'),
        row.get('color'),
        row.get('cost'),
        int(row.get('inkable', False)),
        row.get('strength'),
        row.get('willpower'),
        row.get('lore'),
        row.get('move_cost'),
        row.get('rarity'),
        row.get('franchise'),
        json.dumps(row.get('classifications', [])),
        row.get('body_text'),
        row.get('flavor_text'),
        json.dumps(row.get('abilities', [])),
        row.get('artist'),
        row.get('image'),
        json.dumps(row.get('gamemode', [])),
        row.get('date_added'),
        row.get('date_modified'),
        json.dumps(row.get('card_variants', [])),
        0
    ))

    if ((_ + 1) % 100 == 0) or _ == len(df) - 1:
        print(f"  ⏳ Processate {_ + 1}/{len(df)} carte...")

conn.commit()
conn.close()

print("\n" + "=" * 70)
print("✅ DATABASE CREATO CON SUCCESSO DA JSON LOCALE!")
print("=" * 70)
print(f"\n📊 Carte importate: {len(df)}")
print("\n💡 Per modificare i dati:")
print("   1. Apri 'card.json' con un editor di testo")
print("   2. Cerca la carta (CTRL+F)")
print("   3. Modifica i campi che vuoi")
print("   4. Salva il file")
print("   5. Esegui di nuovo: python main.py")
print("=" * 70)