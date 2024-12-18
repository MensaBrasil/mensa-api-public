-- Registration table
INSERT INTO registration (registration_id, name, expelled, deceased, transferred, cpf, birth_date, profession, gender, join_date, facebook, created_at, updated_at)
VALUES
    (5, 'Fernando Diniz Souza Filho', false, false, false, '12345678901', '2000-01-01', 'Engineer', 'Homem', '2010-01-01', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332');

-- Emails table
INSERT INTO emails (registration_id, email_address, created_at, updated_at)
VALUES
    (5, 'fernando.filho@mensa.org.br', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Phones table
INSERT INTO phones (registration_id, phone_number, created_at, updated_at)
VALUES
    (5, '+552197654322', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Member groups table
INSERT INTO member_groups (registration_id, phone_number, group_id, entry_date, status)
VALUES
    (5, '+552197654322', '120363045725875023@g.us', '2023-10-19', 'Active');

-- Group requests table
INSERT INTO group_requests (registration_id, group_id, no_of_attempts, last_attempt, fulfilled)
VALUES
    (5, '120363150360123420@g.us', '3', '2023-10-01', false),
    (5, '120363115167512889@g.us', '2', '2023-09-25', false),
    (5, '556184020538-1393452040@g.us', '1', '2023-09-20', false),
    (5, '120363044979103954@g.us', '0', NULL, false),
    (5, '120363045725875023@g.us', '1', '2023-09-10', true),
    (5, '120363025301625133@g.us', '3', '2023-09-05', false);

-- Group list table
INSERT INTO group_list (group_name, group_id)
VALUES
    ('Grupos Regionais Mensa Brasil', '120363150360123420@g.us'),
    ('Mensa Bahia Regional', '120363115167512889@g.us'),
    ('Mensa DF Regional', '556184020538-1393452040@g.us'),
    ('Mensa Rio Grande do Sul Regional', '120363044979103954@g.us'),
    ('Mensa Rio de Janeiro Regional', '120363045725875023@g.us'),
    ('Mensampa Regional', '120363025301625133@g.us');
