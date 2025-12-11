-- Indeksy dla poprawy wydajności
CREATE INDEX idx_games_title ON Games(title);
CREATE INDEX idx_games_price ON Games(price);
CREATE INDEX idx_games_developer ON Games(developer_id);

CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);

CREATE INDEX idx_library_user ON Library(user_id);
CREATE INDEX idx_library_game ON Library(game_id);

CREATE INDEX idx_orders_user ON Orders(user_id);
CREATE INDEX idx_orders_date ON Orders(order_date DESC);

CREATE INDEX idx_reviews_game ON Reviews(game_id);
CREATE INDEX idx_reviews_rating ON Reviews(rating DESC);
CREATE INDEX idx_reviews_user_game ON Reviews(user_id, game_id);

CREATE INDEX idx_gamecategories_game ON GameCategories(game_id);
CREATE INDEX idx_gamecategories_category ON GameCategories(category_id);