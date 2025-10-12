import requests
import pandas as pd
import sqlite3
import json

# step 1: Fetch data from the API
print("\n📥 Download dati dall'API...")
url = "https://api.lorcana-api.com/bulk/cards"
response = requests.get(url)
data = response.json()
with open("card.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("✅ Dati scaricati e salvati in card.json")

# step 2: Convert JSON data to a pandas DataFrame
df = pd.json_normalize(data)
print(f"✅ Caricare dati in DataFrame con {len(df)} carte")
df.columns = df.columns.str.lower()

# step 3: Connect to SQLite database (or create it if it doesn't exist)
print("\n📥 Connessione al database SQLite...")
conn = sqlite3.connect('lorcana_cards.db')
cursor = conn.cursor()
# step 4: Create a table to store the card data
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

# step 5: Insert data into the table
print("\n📥 Inserimento dati nel database..."  )

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

    if ((_ + 1) % 100 == 0) or _== len(df) - 1:
        print(f"  ⏳ Processate {_ + 1}/{len(df)} carte...")

    conn.commit()
    

print("\n" + "=" * 70)
print("✅ DATABASE CREATO CON SUCCESSO!")
print("=" * 70)
