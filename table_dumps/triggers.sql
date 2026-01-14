-- Trigger 1: Aktualizacja salda po zakupie
CREATE OR REPLACE FUNCTION update_wallet_after_order()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE Users 
        SET wallet_balance = wallet_balance - NEW.total_amount 
        WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_wallet
AFTER UPDATE ON Orders
FOR EACH ROW
EXECUTE FUNCTION update_wallet_after_order();

-- Trigger 2: Walidacja oceny
CREATE OR REPLACE FUNCTION validate_rating()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.rating < 1 OR NEW.rating > 10 THEN
        RAISE EXCEPTION 'Rating must be between 1 and 10';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_rating
BEFORE INSERT OR UPDATE ON Reviews
FOR EACH ROW
EXECUTE FUNCTION validate_rating();

-- Trigger 3: Aktualizacja czasu gry
CREATE OR REPLACE FUNCTION update_playtime()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Library 
    SET total_playtime = total_playtime + 30  -- przykładowo 30 minut
    WHERE user_id = NEW.user_id AND game_id = NEW.game_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_playtime
AFTER INSERT ON Library
FOR EACH ROW
EXECUTE FUNCTION update_playtime();