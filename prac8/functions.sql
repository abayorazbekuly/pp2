CREATE OR REPLACE FUNCTION search_contacts(pattern_text TEXT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern_text || '%'
       OR p.phone ILIKE '%' || pattern_text || '%'
    ORDER BY p.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, offs INT)
RETURNS TABLE(contact_id INT, contact_name VARCHAR, contact_phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT lim OFFSET offs;
END;
$$ LANGUAGE plpgsql;