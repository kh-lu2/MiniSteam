-- Procedura 1: Dodaj grę do biblioteki użytkownika
CREATE OR REPLACE PROCEDURE add_game_to_library(
    p_user_id INT,
    p_game_id INT,
    p_purchase_price DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = p_user_id) THEN
        RAISE EXCEPTION 'Użytkownik o ID % nie istnieje', p_user_id;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM Games WHERE game_id = p_game_id) THEN
        RAISE EXCEPTION 'Gra o ID % nie istnieje', p_game_id;
    END IF;
    
    IF EXISTS (SELECT 1 FROM Library WHERE user_id = p_user_id AND game_id = p_game_id) THEN
        RAISE EXCEPTION 'Gra jest już w bibliotece użytkownika';
    END IF;
    
    INSERT INTO Library (user_id, game_id, purchase_date, purchase_price, total_playtime, last_played)
    VALUES (p_user_id, p_game_id, CURRENT_DATE, p_purchase_price, 0, NULL);
    
    RAISE NOTICE 'Gra % dodana do biblioteki użytkownika %', p_game_id, p_user_id;
END;
$$;

-- Procedura 2: Zaktualizuj czas gry
CREATE OR REPLACE PROCEDURE update_playtime(
    p_user_id INT,
    p_game_id INT,
    p_minutes_played INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_playtime INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Library WHERE user_id = p_user_id AND game_id = p_game_id) THEN
        RAISE EXCEPTION 'Gra % nie znajduje się w bibliotece użytkownika %', p_game_id, p_user_id;
    END IF;
    
    SELECT total_playtime INTO v_current_playtime
    FROM Library
    WHERE user_id = p_user_id AND game_id = p_game_id;
    
    UPDATE Library
    SET total_playtime = v_current_playtime + p_minutes_played,
        last_played = CURRENT_DATE
    WHERE user_id = p_user_id AND game_id = p_game_id;
    
    RAISE NOTICE 'Zaktualizowano czas gry: dodano % minut (łącznie: % minut)', 
                 p_minutes_played, v_current_playtime + p_minutes_played;
END;
$$;

-- Procedura 3: Utwórz zamówienie z pozycjami
CREATE OR REPLACE PROCEDURE create_order_with_items(
    p_user_id INT,
    p_game_ids INT[],
    p_prices DECIMAL[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id INT;
    v_total_amount DECIMAL := 0;
    v_game_id INT;
    v_price DECIMAL;
    v_index INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = p_user_id) THEN
        RAISE EXCEPTION 'Użytkownik o ID % nie istnieje', p_user_id;
    END IF;
    
    IF array_length(p_game_ids, 1) != array_length(p_prices, 1) THEN
        RAISE EXCEPTION 'Liczba gier i cen musi być taka sama';
    END IF;
    
    FOR v_index IN 1..array_length(p_game_ids, 1)
    LOOP
        v_total_amount := v_total_amount + p_prices[v_index];
    END LOOP;
    
    INSERT INTO Orders (user_id, order_date, total_amount, status)
    VALUES (p_user_id, CURRENT_TIMESTAMP, v_total_amount, 'completed')
    RETURNING order_id INTO v_order_id;
    
    FOR v_index IN 1..array_length(p_game_ids, 1)
    LOOP
        v_game_id := p_game_ids[v_index];
        v_price := p_prices[v_index];
        
        IF NOT EXISTS (SELECT 1 FROM Games WHERE game_id = v_game_id) THEN
            RAISE EXCEPTION 'Gra o ID % nie istnieje', v_game_id;
        END IF;
        
        INSERT INTO OrderItems (order_id, game_id, price, quantity)
        VALUES (v_order_id, v_game_id, v_price, 1);
        
        CALL add_game_to_library(p_user_id, v_game_id, v_price);
    END LOOP;
    
    RAISE NOTICE 'Zamówienie % utworzone: % gier za łączną kwotę %', 
                 v_order_id, array_length(p_game_ids, 1), v_total_amount;
END;
$$;
