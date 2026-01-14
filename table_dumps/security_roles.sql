CREATE ROLE admin_role WITH LOGIN;
CREATE ROLE developer_role WITH LOGIN;
CREATE ROLE user_role WITH LOGIN;

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;

-- Administrator
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA public TO admin_role;

-- Developer
GRANT SELECT, INSERT, UPDATE ON TABLE Games TO developer_role;
GRANT SELECT ON TABLE Categories, Developers TO developer_role;
GRANT SELECT, INSERT, DELETE ON TABLE GameCategories TO developer_role;
GRANT SELECT ON TABLE Library, Reviews, OrderItems TO developer_role;
GRANT USAGE ON SEQUENCE games_game_id_seq TO developer_role;

-- Użytkownik
GRANT SELECT ON TABLE Games, Categories, Developers, GameCategories TO user_role;
GRANT SELECT, INSERT, UPDATE ON TABLE Library TO user_role;
GRANT SELECT, INSERT ON TABLE Orders, OrderItems TO user_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE Reviews TO user_role;
GRANT UPDATE (wallet_balance) ON TABLE Users TO user_role;
GRANT USAGE ON SEQUENCE orders_order_id_seq, reviews_review_id_seq TO user_role;


ALTER TABLE Library ENABLE ROW LEVEL SECURITY;
ALTER TABLE Orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE Games ENABLE ROW LEVEL SECURITY;

-- Użytkownik
CREATE POLICY user_library_policy ON Library
    FOR ALL TO user_role
    USING (user_id = current_setting('app.user_id', true)::INT);

CREATE POLICY user_orders_policy ON Orders
    FOR ALL TO user_role
    USING (user_id = current_setting('app.user_id', true)::INT);

-- Developer
CREATE POLICY developer_games_select ON Games
    FOR SELECT TO developer_role
    USING (true);

CREATE POLICY developer_games_modify ON Games
    FOR INSERT TO developer_role
    WITH CHECK (developer_id = current_setting('app.developer_id', true)::INT);

CREATE POLICY developer_games_update ON Games
    FOR UPDATE TO developer_role
    USING (developer_id = current_setting('app.developer_id', true)::INT);

-- Admin
CREATE POLICY admin_bypass ON Library FOR ALL TO admin_role USING (true);
CREATE POLICY admin_orders_bypass ON Orders FOR ALL TO admin_role USING (true);
CREATE POLICY admin_games_bypass ON Games FOR ALL TO admin_role USING (true);


CREATE USER steam_admin WITH PASSWORD 'SecureAdmin#2026!';
CREATE USER game_developer WITH PASSWORD 'SecureDev#2026!';
CREATE USER regular_user WITH PASSWORD 'SecureUser#2026!';

GRANT admin_role TO steam_admin;
GRANT developer_role TO game_developer;
GRANT user_role TO regular_user;
