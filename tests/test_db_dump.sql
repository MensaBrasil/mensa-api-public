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


-- Registration table
INSERT INTO registration (registration_id, name, expelled, deceased, transferred, cpf, birth_date, profession, gender, join_date, facebook, created_at, updated_at)
VALUES
    (6, 'Inimigos da HP', false, false, false, '12345678901', '1985-07-15', 'Musician', 'Homem', '2005-09-12', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332');

-- Emails table
INSERT INTO emails (registration_id, email_address, created_at, updated_at)
VALUES
    (6, 'calvin@mensa.org.br', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Phones table
INSERT INTO phones (registration_id, phone_number, created_at, updated_at)
VALUES
    (6, '+552198765432', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Member groups table
INSERT INTO member_groups (registration_id, phone_number, group_id, entry_date, status)
VALUES
    (6, '+552198765432', '120363025301625133@g.us', '2023-10-19', 'Active');

-- Group requests table
INSERT INTO group_requests (registration_id, group_id, no_of_attempts, last_attempt, fulfilled)
VALUES
    (6, '120363150360123420@g.us', '2', '2023-10-01', false),
    (6, '120363115167512889@g.us', '1', '2023-09-25', false),
    (6, '556184020538-1393452040@g.us', '1', '2023-09-20', false),
    (6, '120363044979103954@g.us', '0', NULL, false),
    (6, '120363025301625133@g.us', '1', '2023-09-10', true);

-- Additional data for IAM tests

-- Roles table
INSERT INTO iam_roles (role_name, role_description)
VALUES
    ('Diretor Regional', 'Diretor Regional da Mensa Brasil. Responsável pela gestão regional da Mensa Brasil. Representa a Mensa Brasil em eventos nacionais e internacionais.'),
    ('Tesoureiro', 'Tesoureiro da Mensa Brasil. Responsável pela gestão financeira da Mensa Brasil. Controla as finanças da Mensa Brasil e presta contas à diretoria.'),
    ('Diretor De Marketing', 'Diretor de Marketing da Mensa Brasil. Responsável pela divulgação da Mensa Brasil. Cuida da imagem da Mensa Brasil e promove eventos e ações de marketing.'),
    ('Secretário', 'Secretário da Mensa Brasil. Responsável pela documentação da Mensa Brasil. Registra as reuniões e eventos da Mensa Brasil e mantém a documentação atualizada.');

-- Groups table
INSERT INTO iam_groups (group_name, group_description)
VALUES
    ('Beta Tester', 'Grupo de testadores beta da Mensa Brasil.'),
    ('Sig Matemática', 'Grupo de interesse especial em matemática da Mensa Brasil.');

-- Permissions table
INSERT INTO iam_permissions (permission_name, permission_description)
VALUES
    ('create_event', 'Can create events.'),
    ('edit_event', 'Can edit events.'),
    ('delete_event', 'Can delete events.'),
    ('whatsapp_bot', 'Can interact with the WhatsApp bot.');

-- Role assignments table
INSERT INTO iam_user_roles_map (role_id, registration_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'Diretor Regional'), 5);

INSERT INTO iam_user_roles_map (role_id, registration_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'Diretor De Marketing'), 5);

-- Group assignments table
INSERT INTO iam_user_groups_map (group_id, registration_id)
VALUES
    ((SELECT id FROM iam_groups WHERE group_name = 'Beta Tester'), 5);

-- Role permissions table
INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'Diretor Regional'), (SELECT id FROM iam_permissions WHERE permission_name = 'create_event'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'Diretor De Marketing'), (SELECT id FROM iam_permissions WHERE permission_name = 'delete_event'));

-- Group permissions table
INSERT INTO iam_group_permissions_map (group_id, permission_id)
VALUES
    ((SELECT id FROM iam_groups WHERE group_name = 'Beta Tester'), (SELECT id FROM iam_permissions WHERE permission_name = 'whatsapp_bot'));
