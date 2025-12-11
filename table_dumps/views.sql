-- Widok 1: Gry z developerami i kategoriami
CREATE VIEW v_game_details AS
SELECT 
    g.game_id,
    g.title,
    g.price,
    d.name AS developer_name,
    g.is_available,
    STRING_AGG(c.name, ', ') AS categories
FROM Games g
JOIN Developers d ON g.developer_id = d.developer_id
LEFT JOIN GameCategories gc ON g.game_id = gc.game_id
LEFT JOIN Categories c ON gc.category_id = c.category_id
GROUP BY g.game_id, d.name;

-- Widok 2: Biblioteka użytkownika z informacjami
CREATE VIEW v_user_library AS
SELECT 
    u.username,
    g.title,
    l.purchase_price,
    l.total_playtime,
    ROUND(l.total_playtime::DECIMAL / 60, 1) AS playtime_hours
FROM Library l
JOIN Users u ON l.user_id = u.user_id
JOIN Games g ON l.game_id = g.game_id;

-- Widok 3: Statystyki zamówień
CREATE VIEW v_order_stats AS
SELECT 
    u.username,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent,
    AVG(o.total_amount) AS avg_order_value
FROM Orders o
JOIN Users u ON o.user_id = u.user_id
WHERE o.status = 'completed'
GROUP BY u.user_id;

-- Widok 4: Recenzje z informacjami
CREATE VIEW v_reviews_detailed AS
SELECT 
    u.username,
    g.title,
    r.rating,
    r.is_verified_owner,
    r.review_date
FROM Reviews r
JOIN Users u ON r.user_id = u.user_id
JOIN Games g ON r.game_id = g.game_id;