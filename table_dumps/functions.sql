-- Funkcja 1: Statystyki użytkownika
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id INT)
RETURNS TABLE (
    username VARCHAR,
    total_games INT,
    total_playtime_hours DECIMAL,
    total_spent DECIMAL,
    avg_rating DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.username,
        COUNT(DISTINCT l.game_id)::INT,
        ROUND(COALESCE(SUM(l.total_playtime)::DECIMAL / 60, 0), 1),
        COALESCE(SUM(l.purchase_price), 0),
        ROUND(COALESCE(AVG(r.rating), 0), 2)
    FROM Users u
    LEFT JOIN Library l ON u.user_id = l.user_id
    LEFT JOIN Reviews r ON u.user_id = r.user_id
    WHERE u.user_id = p_user_id
    GROUP BY u.user_id;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 2: Popularne gry (top N)
CREATE OR REPLACE FUNCTION get_popular_games(limit_count INT)
RETURNS TABLE (
    title VARCHAR,
    developer VARCHAR,
    owners_count BIGINT,
    avg_rating DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.title,
        d.name,
        COUNT(l.library_id),
        ROUND(AVG(r.rating), 2)
    FROM Games g
    JOIN Developers d ON g.developer_id = d.developer_id
    LEFT JOIN Library l ON g.game_id = l.game_id
    LEFT JOIN Reviews r ON g.game_id = r.game_id
    GROUP BY g.game_id, d.name
    ORDER BY COUNT(l.library_id) DESC, AVG(r.rating) DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 3: Gry w kategorii
CREATE OR REPLACE FUNCTION get_games_by_category(category_name VARCHAR)
RETURNS TABLE (
    title VARCHAR,
    developer VARCHAR,
    price DECIMAL,
    avg_rating DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.title,
        d.name,
        g.price,
        ROUND(AVG(r.rating), 2)
    FROM Games g
    JOIN Developers d ON g.developer_id = d.developer_id
    JOIN GameCategories gc ON g.game_id = gc.game_id
    JOIN Categories c ON gc.category_id = c.category_id
    LEFT JOIN Reviews r ON g.game_id = r.game_id
    WHERE c.name = category_name
    GROUP BY g.game_id, d.name
    ORDER BY AVG(r.rating) DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;