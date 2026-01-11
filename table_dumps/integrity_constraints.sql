-- Check 1: Cena gry nie może być ujemna
ALTER TABLE Games
ADD CONSTRAINT chk_games_price_positive 
CHECK (price >= 0);

-- Check 2: Ocena w recenzji musi być w zakresie 1-10
ALTER TABLE Reviews
ADD CONSTRAINT chk_reviews_rating_range 
CHECK (rating >= 1 AND rating <= 10);

-- Check 3: Saldo portfela nie może być ujemne
ALTER TABLE Users
ADD CONSTRAINT chk_users_wallet_positive 
CHECK (wallet_balance >= 0);

-- Check 4: Cena zakupu w bibliotece nie może być ujemna
ALTER TABLE Library
ADD CONSTRAINT chk_library_purchase_price_positive 
CHECK (purchase_price >= 0);

-- Check 5: Czas gry nie może być ujemny
ALTER TABLE Library
ADD CONSTRAINT chk_library_playtime_positive 
CHECK (total_playtime >= 0);

-- Check 6: Całkowita kwota zamówienia nie może być ujemna
ALTER TABLE Orders
ADD CONSTRAINT chk_orders_total_positive 
CHECK (total_amount >= 0);

-- Check 7: Status zamówienia musi być jedną z dozwolonych wartości
ALTER TABLE Orders
ADD CONSTRAINT chk_orders_status_valid 
CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded'));

-- Check 8: Email musi zawierać znak @
ALTER TABLE Users
ADD CONSTRAINT chk_users_email_format 
CHECK (email LIKE '%@%');

-- Unique 1: Użytkownik może mieć tylko jedną recenzję dla danej gry
ALTER TABLE Reviews
ADD CONSTRAINT uq_reviews_user_game 
UNIQUE (user_id, game_id);

-- Unique 2: Użytkownik może mieć grę w bibliotece tylko raz
ALTER TABLE Library
ADD CONSTRAINT uq_library_user_game 
UNIQUE (user_id, game_id);
