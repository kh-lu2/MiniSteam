import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Game Store DB (Full)", layout="wide", page_icon="🎮")

# --- STYLE CSS ---
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d0d0d0;
    }
    div[data-testid="stMetric"] label { color: #000000 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #000000 !important; }
    .stDataFrame { border: 1px solid #e0e0e0; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE DATY ---
def date_days_ago(days):
    return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

# --- PRZYGOTOWANIE BAZY DANYCH (SQLite) ---
@st.cache_resource
def init_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    c = conn.cursor()

    # 1. TWORZENIE TABEL (Wszystkie tabele z Twoich plików)
    c.executescript("""
        CREATE TABLE Developers (developer_id INTEGER PRIMARY KEY, name VARCHAR(100));
        CREATE TABLE Categories (category_id INTEGER PRIMARY KEY, name VARCHAR(50));
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY, 
            username VARCHAR(50), 
            email VARCHAR(100), 
            password_hash VARCHAR(255), 
            wallet_balance DECIMAL(10,2)
        );
        CREATE TABLE Games (
            game_id INTEGER PRIMARY KEY,
            title VARCHAR(100),
            price DECIMAL(10,2),
            developer_id INT REFERENCES Developers(developer_id),
            is_available BOOLEAN DEFAULT 1
        );
        CREATE TABLE GameCategories (
            game_id INT REFERENCES Games(game_id),
            category_id INT REFERENCES Categories(category_id),
            PRIMARY KEY (game_id, category_id)
        );
        CREATE TABLE Library (
            library_id INTEGER PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            game_id INT REFERENCES Games(game_id),
            purchase_price DECIMAL(10,2),
            total_playtime INTEGER
        );
        CREATE TABLE Orders (
            order_id INTEGER PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            order_date TIMESTAMP,
            total_amount DECIMAL(10,2),
            status VARCHAR(20)
        );
        CREATE TABLE OrderItems (
            order_item_id INTEGER PRIMARY KEY,
            order_id INT REFERENCES Orders(order_id),
            game_id INT REFERENCES Games(game_id),
            price DECIMAL(10,2)
        );
        CREATE TABLE Reviews (
            review_id INTEGER PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            game_id INT REFERENCES Games(game_id),
            rating INTEGER,
            review_date TIMESTAMP,
            is_verified_owner BOOLEAN
        );
    """)
    
    # 2. WSTAWIANIE PEŁNYCH DANYCH
    
    # -- Deweloperzy (41 pozycji) --
    developers = [
        (1, 'Valve'), (2, 'Rockstar Games'), (3, 'Ubisoft'), (4, 'Bethesda Softworks'), 
        (5, 'CD Projekt Red'), (6, 'Naughty Dog'), (7, 'Blizzard Entertainment'), (8, 'Electronic Arts'), 
        (9, 'Square Enix'), (10, 'BioWare'), (11, 'Capcom'), (12, 'Konami'), (13, 'Activision'), 
        (14, 'id Software'), (15, 'Bandai Namco Studios'), (16, 'Sega'), (17, 'FromSoftware'), 
        (18, 'Rocksteady Studios'), (19, '2K Games'), (20, 'Telltale Games'), (21, 'Respawn Entertainment'),
        (22, 'Riot Games'), (23, 'ArenaNet'), (24, 'LucasArts'), (25, 'IO Interactive'), 
        (26, 'Blizzard North'), (27, 'EA Sports'), (28, 'Bethesda Game Studios'), (29, 'CD Projekt'), 
        (30, 'Valve South'), (31, 'Ubisoft Montreal'), (32, 'Epic Games'), (33, 'Gearbox Software'),
        (34, 'Infinity Ward'), (35, 'Rare'), (36, 'Maxis'), (37, 'Crytek'), (38, 'DICE'),
        (39, 'Insomniac Games'), (40, 'Obsidian Entertainment'), (41, 'Square Enix Europe')
    ]
    c.executemany("INSERT INTO Developers VALUES (?,?)", developers)

    # -- Kategorie --
    categories = [(1, 'Action'), (2, 'RPG'), (3, 'Shooter'), (4, 'FPS'), (5, 'Adventure'), (6, 'MOBA'), (7, 'Sports'), (8, 'Strategy'), (9, 'Simulation')]
    c.executemany("INSERT INTO Categories VALUES (?,?)", categories)

    # -- Użytkownicy --
    users = [
        (1, 'SummonerOne', 'summoner1@lolmail.com', 'hash1', 150.00),
        (2, 'GamerGirl42', 'gg42@example.com', 'hash2', 75.50),
        (3, 'RetroPlayer', 'retro@example.com', 'hash3', 20.00),
        (4, 'ProNoob', 'pronoob@example.com', 'hash4', 300.00),
        (5, 'CasualJoe', 'casualjoe@example.com', 'hash5', 5.00),
        (6, 'EliteGamer', 'elite@example.com', 'hash6', 500.00),
        (7, 'FunTimes', 'funtimes@example.com', 'hash7', 25.00),
        (8, 'Strategist', 'strategist@example.com', 'hash8', 80.00),
        (9, 'RoguePlayer', 'rogue@example.com', 'hash9', 120.00),
        (10, 'ArcadeFan', 'arcadefan@example.com', 'hash10', 60.00)
    ]
    c.executemany("INSERT INTO Users VALUES (?,?,?,?,?)", users)

    # -- Gry (PEŁNE 100 POZYCJI) --
    games_data = [
        (1, 'Half-Life 2', 9.99, 1), (2, 'Portal 2', 14.99, 1), (3, 'Dota 2', 0.00, 1), (4, 'Counter-Strike: Global Offensive', 14.99, 1), (5, 'Left 4 Dead 2', 9.99, 1),
        (6, 'Grand Theft Auto V', 29.99, 2), (7, 'Red Dead Redemption 2', 59.99, 2), (8, 'L.A. Noire', 19.99, 2), (9, 'Bully', 9.99, 2),
        (10, 'Assassin''s Creed Valhalla', 49.99, 3), (11, 'Far Cry 6', 39.99, 3), (12, 'Rainbow Six Siege', 19.99, 3), (13, 'Watch Dogs 2', 24.99, 3), (14, 'The Division 2', 29.99, 3),
        (15, 'The Elder Scrolls V: Skyrim', 39.99, 4), (16, 'Fallout 4', 29.99, 4), (17, 'Dishonored 2', 24.99, 4), (18, 'Doom (2016)', 19.99, 4), (19, 'The Elder Scrolls IV: Oblivion', 19.99, 4),
        (20, 'The Witcher 3: Wild Hunt', 34.99, 5), (21, 'Cyberpunk 2077', 49.99, 5), (22, 'Gwent: The Witcher Card Game', 0.00, 5), (23, 'The Witcher 2: Assassins of Kings', 14.99, 5),
        (24, 'The Last of Us Part II', 39.99, 6), (25, 'Uncharted 4: A Thief''s End', 29.99, 6), (26, 'Uncharted: The Lost Legacy', 19.99, 6), (27, 'Uncharted 3: Drake''s Deception', 19.99, 6), (28, 'Uncharted: Drake''s Fortune', 9.99, 6),
        (29, 'Overwatch', 19.99, 7), (30, 'World of Warcraft', 14.99, 7), (31, 'Diablo III', 19.99, 7), (32, 'Diablo II: Resurrected', 19.99, 7), (33, 'Starcraft II', 29.99, 7),
        (34, 'FIFA 21', 49.99, 8), (35, 'Madden NFL 21', 49.99, 8), (36, 'The Sims 4', 39.99, 8), (37, 'Battlefield V', 29.99, 8), (38, 'Need for Speed Heat', 29.99, 8),
        (39, 'Final Fantasy VII Remake', 59.99, 9), (40, 'Kingdom Hearts III', 39.99, 9), (41, 'Tomb Raider (2013)', 19.99, 9), (42, 'Final Fantasy XV', 39.99, 9), (43, 'NieR: Automata', 29.99, 9),
        (44, 'Mass Effect Legendary Edition', 49.99, 10), (45, 'Dragon Age: Inquisition', 29.99, 10), (46, 'Mass Effect 2', 9.99, 10), (47, 'Dragon Age: Origins', 14.99, 10),
        (48, 'Resident Evil 2 Remake', 19.99, 11), (49, 'Monster Hunter: World', 29.99, 11), (50, 'Resident Evil 3 Remake', 19.99, 11), (51, 'Street Fighter V', 19.99, 11),
        (52, 'Metal Gear Solid V: The Phantom Pain', 19.99, 12), (53, 'Pro Evolution Soccer 2021', 49.99, 12), (54, 'Silent Hill 2', 9.99, 12),
        (55, 'Call of Duty: Modern Warfare (2019)', 59.99, 13), (56, 'Call of Duty: Warzone', 0.00, 13), (57, 'Sekiro: Shadows Die Twice', 39.99, 17),
        (58, 'DOOM Eternal', 39.99, 14), (59, 'Wolfenstein II: The New Colossus', 29.99, 14),
        (60, 'Dark Souls III', 29.99, 15), (61, 'Tekken 7', 19.99, 15), (62, 'Ni no Kuni II', 39.99, 15),
        (63, 'Yakuza: Like a Dragon', 39.99, 16), (64, 'Sonic Mania', 19.99, 16), (65, 'Total War: Warhammer II', 29.99, 16),
        (66, 'Elden Ring', 59.99, 17), (67, 'Bloodborne', 29.99, 17), (68, 'Dark Souls', 14.99, 17),
        (69, 'Batman: Arkham Knight', 19.99, 18), (70, 'Batman: Arkham Asylum', 9.99, 18), (71, 'Batman: Arkham City', 14.99, 18),
        (72, 'BioShock Infinite', 14.99, 19), (73, 'XCOM 2', 29.99, 19), (74, 'Civilization VI', 49.99, 19),
        (75, 'The Walking Dead: Season One', 9.99, 20), (76, 'The Walking Dead: Season Two', 9.99, 20), (77, 'The Wolf Among Us', 14.99, 20),
        (78, 'Apex Legends', 0.00, 21), (79, 'Titanfall 2', 19.99, 21), (80, 'Star Wars Jedi: Fallen Order', 39.99, 21),
        (81, 'League of Legends', 0.00, 22), (82, 'Teamfight Tactics', 0.00, 22),
        (83, 'Guild Wars 2', 19.99, 23), (84, 'Guild Wars Nightfall', 9.99, 23),
        (85, 'Star Wars: Knights of the Old Republic', 14.99, 24), (86, 'Monkey Island 2: LeChuck''s Revenge', 9.99, 24),
        (87, 'Hitman 3', 39.99, 25), (88, 'Hitman 2', 29.99, 25),
        (89, 'Diablo', 9.99, 26), (90, 'Diablo II', 14.99, 26),
        (91, 'FIFA 22', 59.99, 27), (92, 'Madden NFL 22', 59.99, 27),
        (93, 'Fallout 76', 29.99, 28), (94, 'The Elder Scrolls Online', 29.99, 28),
        (95, 'The Witcher: Enhanced Edition', 9.99, 29), (96, 'Thronebreaker: The Witcher Tales', 14.99, 29),
        (97, 'Portal', 9.99, 30), (98, 'Left 4 Dead', 9.99, 30), (99, 'Half-Life', 9.99, 30), (100, 'Team Fortress 2', 0.00, 30)
    ]
    # is_available = 1
    games_ready = [(g[0], g[1], g[2], g[3], 1) for g in games_data]
    c.executemany("INSERT OR REPLACE INTO Games VALUES (?,?,?,?,?)", games_ready)

    # -- GameCategories (PEŁNA LISTA) --
    game_cats = [
        (1,1),(1,3),(1,4),(2,5),(3,6),(4,3),(4,4),(5,1),(5,3),
        (6,1),(6,5),(7,1),(7,5),(8,5),(9,5),
        (10,5),(10,1),(11,1),(11,3),(12,3),(12,4),(13,1),(13,5),(14,1),(14,3),
        (15,2),(15,5),(16,2),(17,1),(17,5),(18,1),(18,3),(18,4),(19,2),
        (20,2),(20,5),(21,2),(21,5),(22,8),(23,2),(23,5),
        (24,5),(25,5),(26,5),(27,5),(28,5),
        (29,1),(29,3),(30,9),(31,2),(31,1),(32,2),(32,1),(33,8),
        (34,7),(35,7),(36,9),(37,3),(38,1),
        (39,2),(39,5),(40,2),(41,5),(42,2),(43,1),(43,2),
        (44,2),(45,2),(46,2),(47,2),
        (48,1),(48,5),(49,1),(50,1),(51,1),
        (52,1),(52,5),(53,7),(54,5),
        (55,3),(55,4),(56,3),(56,4),(57,1),(57,2),(57,5),
        (58,1),(58,3),(58,4),(59,1),(59,3),(59,4),
        (60,2),(60,1),(61,1),(62,2),(62,5),
        (63,5),(63,1),(64,1),(65,8),
        (66,2),(66,1),(67,2),(67,1),(68,2),(68,1),
        (69,1),(69,5),(70,5),(71,5),
        (72,5),(72,1),(73,8),(74,8),(74,9),
        (75,5),(76,5),(77,5),
        (78,3),(78,4),(79,3),(79,4),(80,5),
        (81,6),(82,8),(83,2),(83,8),(84,5),
        (85,2),(85,5),(86,5),(87,1),(87,5),(88,1),(88,5),
        (89,2),(89,1),(90,2),(90,1),(91,7),(92,7),(93,2),(93,9),(94,9),
        (95,2),(96,2),(97,5),(98,1),(99,1),(100,1),(100,3)
    ]
    c.executemany("INSERT OR IGNORE INTO GameCategories VALUES (?,?)", game_cats)

    # -- Library (PEŁNA LISTA) --
    library_data = [
        (1, 3, 0.00, 5400), (1, 4, 14.99, 800), (1, 81, 0.00, 2000), (1, 1, 9.99, 600),
        (2, 7, 59.99, 1200), (2, 12, 19.99, 700), (2, 39, 59.99, 300),
        (3, 41, 19.99, 900), (3, 12, 19.99, 300), (3, 86, 9.99, 120),
        (4, 1, 9.99, 800), (4, 55, 59.99, 400), (4, 78, 0.00, 600),
        (5, 50, 0.00, 240), (5, 38, 29.99, 30),
        (6, 20, 34.99, 9999), (6, 66, 59.99, 7000), (6, 58, 39.99, 5000),
        (7, 40, 29.99, 100), (7, 61, 19.99, 200), (7, 83, 19.99, 600),
        (8, 74, 49.99, 1000), (8, 73, 29.99, 500), (8, 65, 29.99, 700),
        (9, 95, 9.99, 600), (9, 78, 0.00, 500), (9, 32, 19.99, 200),
        (10, 45, 14.99, 1200), (10, 64, 19.99, 800), (10, 87, 39.99, 300)
    ]
    c.executemany("INSERT INTO Library (user_id, game_id, purchase_price, total_playtime) VALUES (?,?,?,?)", library_data)

    # -- Orders (NOWE) --
    # Symulacja dat dla SQLite (zamiast NOW() - INTERVAL)
    orders = [
        (1, 1, date_days_ago(10), 24.98, 'completed'),
        (2, 2, date_days_ago(2), 149.97, 'completed'),
        (3, 3, date_days_ago(5), 29.98, 'canceled'),
        (4, 4, date_days_ago(1), 69.98, 'completed'),
        (5, 5, date_days_ago(0), 29.99, 'pending')
    ]
    c.executemany("INSERT INTO Orders VALUES (?,?,?,?,?)", orders)

    # -- OrderItems (NOWE) --
    order_items = [
        (1, 1, 3, 0.00), (2, 1, 4, 14.99),
        (3, 2, 7, 59.99), (4, 2, 12, 19.99), (5, 2, 39, 59.99),
        (6, 3, 41, 19.99), (7, 3, 12, 10.00),
        (8, 4, 1, 9.99), (9, 4, 55, 59.99), (10, 4, 78, 0.00),
        (11, 5, 50, 0.00)
    ]
    c.executemany("INSERT INTO OrderItems VALUES (?,?,?,?)", order_items)

    # -- Reviews (NOWE) --
    reviews = [
        (1, 1, 3, 10, date_days_ago(30), 1), (2, 1, 4, 9, date_days_ago(15), 1), (3, 1, 81, 8, date_days_ago(10), 1), (4, 1, 1, 9, date_days_ago(20), 1),
        (5, 2, 7, 9, date_days_ago(10), 1), (6, 2, 12, 7, date_days_ago(5), 1), (7, 2, 39, 8, date_days_ago(2), 1),
        (8, 3, 41, 6, date_days_ago(20), 0), (9, 3, 12, 7, date_days_ago(15), 1), (10, 3, 86, 9, date_days_ago(10), 1),
        (11, 4, 1, 8, date_days_ago(5), 1), (12, 4, 55, 7, date_days_ago(2), 1), (13, 4, 78, 9, date_days_ago(1), 1),
        (14, 5, 50, 7, date_days_ago(3), 1), (15, 5, 38, 5, date_days_ago(1), 1),
        (16, 6, 20, 10, date_days_ago(2), 1), (17, 6, 66, 10, date_days_ago(5), 1), (18, 6, 58, 9, date_days_ago(7), 1),
        (19, 7, 40, 7, date_days_ago(10), 1), (20, 7, 61, 6, date_days_ago(8), 1), (21, 7, 83, 8, date_days_ago(3), 1),
        (22, 8, 74, 9, date_days_ago(6), 1), (23, 8, 73, 8, date_days_ago(5), 1), (24, 8, 65, 9, date_days_ago(2), 1),
        (25, 9, 95, 7, date_days_ago(4), 1), (26, 9, 78, 9, date_days_ago(3), 1), (27, 9, 32, 8, date_days_ago(5), 1),
        (28, 10, 45, 8, date_days_ago(1), 1), (29, 10, 64, 6, date_days_ago(2), 1), (30, 10, 87, 9, date_days_ago(1), 1),
        (31, 1, 20, 10, date_days_ago(7), 1), (32, 2, 1, 8, date_days_ago(21), 0), (33, 3, 3, 7, date_days_ago(60), 0),
        (34, 4, 81, 9, date_days_ago(4), 0), (35, 5, 55, 6, date_days_ago(1), 0), (36, 6, 78, 10, date_days_ago(3), 1),
        (37, 7, 12, 7, date_days_ago(2), 1), (38, 8, 1, 9, date_days_ago(5), 1), (39, 9, 66, 10, date_days_ago(2), 1),
        (40, 10, 81, 8, date_days_ago(1), 1)
    ]
    c.executemany("INSERT INTO Reviews VALUES (?,?,?,?,?,?)", reviews)

    conn.commit()
    return conn

conn = init_db()

# --- SIDEBAR ---
st.sidebar.title("🎮 Panel Admina")
page = st.sidebar.radio("Nawigacja:", ["Lista Gier", "Znajdź Użytkownika", "Statystyki"])

# --- WIDOK 1: LISTA GIER ---
if page == "Lista Gier":
    st.title("📚 Lista Gier w Bazie (100 pozycji)")
    
    search_term = st.text_input("🔍 Szukaj gry (tytuł):", "")
    
    query = """
    SELECT 
        g.game_id AS ID,
        g.title AS "Tytuł", 
        d.name AS "Deweloper", 
        g.price AS "Cena ($)",
        GROUP_CONCAT(c.name, ', ') as "Kategorie"
    FROM Games g
    JOIN Developers d ON g.developer_id = d.developer_id
    LEFT JOIN GameCategories gc ON g.game_id = gc.game_id
    LEFT JOIN Categories c ON gc.category_id = c.category_id
    WHERE g.title LIKE ?
    GROUP BY g.game_id
    ORDER BY g.game_id
    """
    
    df = pd.read_sql(query, conn, params=(f"%{search_term}%",))
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- WIDOK 2: WYSZUKIWANIE UŻYTKOWNIKA ---
elif page == "Znajdź Użytkownika":
    st.title("👤 Profil Użytkownika")
    st.markdown("Wpisz nick gracza, np.: **EliteGamer**, **SummonerOne**, **GamerGirl42**")
    
    search_user = st.text_input("Nick użytkownika:", "")
    
    if search_user:
        user_query = "SELECT * FROM Users WHERE username = ? COLLATE NOCASE"
        user_info = pd.read_sql(user_query, conn, params=(search_user,))
        
        if not user_info.empty:
            user_id = int(user_info['user_id'].values[0])
            username_db = user_info['username'].values[0]
            wallet = user_info['wallet_balance'].values[0]
            email = user_info['email'].values[0]
            
            st.success(f"Znaleziono: {username_db}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Portfel", f"${wallet}")
            with col2:
                st.write(f"📧 **Email:** {email}")
                st.write(f"🆔 **ID:** {user_id}")

            # TABS dla Biblioteki, Zamówień i Recenzji
            tab1, tab2, tab3 = st.tabs(["📚 Biblioteka", "📦 Ostatnie Zamówienia", "⭐ Recenzje"])

            with tab1:
                lib_query = """
                SELECT 
                    g.title AS "Gra", 
                    l.purchase_price AS "Koszt ($)", 
                    ROUND(l.total_playtime / 60.0, 1) AS "Godziny"
                FROM Library l
                JOIN Games g ON l.game_id = g.game_id
                WHERE l.user_id = ?
                ORDER BY l.total_playtime DESC
                """
                lib_df = pd.read_sql(lib_query, conn, params=(user_id,))
                if not lib_df.empty:
                    st.dataframe(lib_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Pusta biblioteka.")

            with tab2:
                ord_query = """
                SELECT 
                    o.order_id AS "ID Zamówienia",
                    o.order_date AS "Data",
                    o.total_amount AS "Kwota ($)",
                    o.status AS "Status"
                FROM Orders o
                WHERE o.user_id = ?
                ORDER BY o.order_date DESC
                """
                ord_df = pd.read_sql(ord_query, conn, params=(user_id,))
                if not ord_df.empty:
                    st.dataframe(ord_df, use_container_width=True, hide_index=True)
                    st.caption("*Szczegóły pozycji w bazie danych OrderItems")
                else:
                    st.info("Brak zamówień.")

            with tab3:
                rev_query = """
                SELECT 
                    g.title AS "Gra",
                    r.rating AS "Ocena",
                    r.review_date AS "Data",
                    CASE WHEN r.is_verified_owner = 1 THEN 'Tak' ELSE 'Nie' END AS "Zakup Potwierdzony"
                FROM Reviews r
                JOIN Games g ON r.game_id = g.game_id
                WHERE r.user_id = ?
                ORDER BY r.review_date DESC
                """
                rev_df = pd.read_sql(rev_query, conn, params=(user_id,))
                if not rev_df.empty:
                    st.dataframe(rev_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Brak recenzji.")

        else:
            st.error(f"❌ Nie znaleziono użytkownika: '{search_user}'")

# --- WIDOK 3: STATYSTYKI ---
elif page == "Statystyki":
    st.title("📊 Analityka Sklepu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Średnie ceny gier (Studia)")
        query_devs = """
        SELECT d.name, AVG(g.price) as avg_price 
        FROM Games g 
        JOIN Developers d ON g.developer_id = d.developer_id 
        GROUP BY d.name
        ORDER BY avg_price DESC
        LIMIT 15
        """
        df_devs = pd.read_sql(query_devs, conn)
        st.bar_chart(df_devs.set_index("name"))

    with col2:
        st.subheader("Średnie ceny gier (Kategorie)")
        query_cats = """
        SELECT c.name, AVG(g.price) as avg_price 
        FROM Games g 
        JOIN GameCategories gc ON g.game_id = gc.game_id
        JOIN Categories c ON gc.category_id = c.category_id
        GROUP BY c.name
        ORDER BY avg_price DESC
        """
        df_cats = pd.read_sql(query_cats, conn)
        st.bar_chart(df_cats.set_index("name"))