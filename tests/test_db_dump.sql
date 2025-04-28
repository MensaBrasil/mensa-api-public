-- Registration table
INSERT INTO registration (registration_id, name, expelled, deceased, transferred, cpf, birth_date, profession, gender, join_date, facebook, created_at, updated_at)
VALUES
    (5, 'Fernando Diniz Souza Filho', false, false, false, '12345678901', '2000-01-01', 'Engineer', 'Homem', '2010-01-01', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (6, 'Inimigos da HP', false, false, false, '12345678901', '1985-07-15', 'Musician', 'Homem', '2005-09-12', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (7, 'Ana Silva Junior', false, false, false, '23456789012', '2012-03-10', 'Student', 'Mulher', '2023-01-15', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (8, 'Pedro Santos', false, false, false, '34567890123', '2008-06-20', 'Student', 'Homem', '2022-11-30', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (9, 'Maria Oliveira', false, false, false, '45678901234', '1995-09-25', 'Teacher', 'Mulher', '2021-08-05', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (10, 'Lucas Costa', false, false, false, '56789012345', '2015-12-05', 'Student', 'Homem', '2023-03-20', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332'),
    (11, 'Carla Ferreira', false, false, false, '67890123456', '1990-04-15', 'Lawyer', 'Mulher', '2020-10-10', NULL, '2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332');

-- Emails table
INSERT INTO emails (registration_id, email_address, email_type, created_at, updated_at)
VALUES
    (5, 'fernando.filho@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (6, 'calvin@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (7, 'ana.junior@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (8, 'pedro.santos@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (9, 'maria.oliveira@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (10, 'lucas.costa@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (11, 'carla.ferreira@mensa.org.br', 'mensa', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Phones table
INSERT INTO phones (registration_id, phone_number, created_at, updated_at)
VALUES
    (5, '+552197654322', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (6, '+552198765432', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (7, '+552199876543', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (8, '+552191234567', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (9, '+552192345678', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (10, '+552193456789', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276'),
    (11, '+552194567890', '2023-08-19 21:47:18.276', '2023-08-19 21:47:18.276');

-- Member groups table
INSERT INTO member_groups (registration_id, phone_number, group_id, entry_date, status)
VALUES
    (5, '+552197654322', '120363045725875023@g.us', '2023-10-19', 'Active'),
    (6, '+552198765432', '120363025301625133@g.us', '2023-10-19', 'Active'),
    (7, '+552199876543', '120363115167512889@g.us', '2023-10-19', 'Active'),
    (8, '+552191234567', '556184020538-1393452040@g.us', '2023-10-19', 'Active'),
    (9, '+552192345678', '120363044979103954@g.us', '2023-10-19', 'Active'),
    (10, '+552193456789', '120363045725875023@g.us', '2023-10-19', 'Active'),
    (11, '+552194567890', '120363025301625133@g.us', '2023-10-19', 'Active');

-- Group requests table
INSERT INTO group_requests (registration_id, group_id, no_of_attempts, last_attempt, fulfilled)
VALUES
    (5, '120363150360123420@g.us', '3', '2023-10-01', false),
    (5, '120363115167512889@g.us', '2', '2023-09-25', false),
    (5, '556184020538-1393452040@g.us', '1', '2023-09-20', false),
    (5, '120363044979103954@g.us', '0', NULL, false),
    (5, '120363045725875023@g.us', '1', '2023-09-10', true),
    (5, '120363025301625133@g.us', '3', '2023-09-05', false),
    (6, '120363150360123420@g.us', '2', '2023-10-01', false),
    (6, '120363115167512889@g.us', '1', '2023-09-25', false),
    (6, '556184020538-1393452040@g.us', '1', '2023-09-20', false),
    (6, '120363044979103954@g.us', '0', NULL, false),
    (6, '120363025301625133@g.us', '1', '2023-09-10', true),
    (7, '120363150360123420@g.us', '1', '2023-10-02', false),
    (7, '120363115167512889@g.us', '1', '2023-09-28', true),
    (8, '556184020538-1393452040@g.us', '2', '2023-09-15', true),
    (9, '120363044979103954@g.us', '1', '2023-09-30', true),
    (10, '120363045725875023@g.us', '3', '2023-10-05', true),
    (11, '120363025301625133@g.us', '2', '2023-09-20', true);

-- Group list table
INSERT INTO group_list (group_name, group_id)
VALUES
    ('Grupos Regionais Mensa Brasil', '120363150360123420@g.us'),
    ('Mensa Bahia Regional', '120363115167512889@g.us'),
    ('Mensa DF Regional', '556184020538-1393452040@g.us'),
    ('Mensa Rio Grande do Sul Regional', '120363044979103954@g.us'),
    ('Mensa Rio de Janeiro Regional', '120363045725875023@g.us'),
    ('Mensampa Regional', '120363025301625133@g.us'),
    ('MB | Mulheres', '120363025301625134@g.us');

-- Membership payments table
INSERT INTO membership_payments (created_at, updated_at, payment_id, registration_id, payment_date, expiration_date, amount_paid, observation, payment_method, transaction_id, payment_status)
VALUES
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 1, 5, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', 180.00, 'Annual membership fee', 'BANK_TRANSFER', 'TRANS123456', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 2, 6, '2023-01-12', '2023-07-12', 100.00, 'Semi-annual membership', 'PIX', 'PIX567890', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 3, 7, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', 180.00, 'Annual membership fee', 'BANK_TRANSFER', 'TRANS345678', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 4, 8, '2023-03-05', '2023-09-05', 100.00, 'Semi-annual membership', 'PIX', 'PIX901234', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 5, 9, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', 180.00, 'Annual membership fee', 'CREDIT_CARD', 'CARD567890', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 6, 10, '2023-04-15', '2023-10-15', 100.00, 'Semi-annual membership', 'PIX', 'PIX234567', 'CONFIRMED'),
    ('2023-08-24 00:03:53.332', '2023-08-24 00:03:53.332', 7, 11, '2023-08-01', '2024-08-01', 180.00, 'Annual membership fee', 'BANK_TRANSFER', 'TRANS678901', 'CONFIRMED');

-- Additional data for IAM tests,
-- Roles table
INSERT INTO iam_roles (role_name, role_description)
VALUES
    ('DIRETOR.REGIONAL', 'Diretor regional da Mensa Brasil. Responsável pela gestão regional da Mensa Brasil. Representa a Mensa Brasil em eventos nacionais e internacionais.'),
    ('TESOUREIRO', 'Tesoureiro da Mensa Brasil. Responsável pela gestão financeira da Mensa Brasil. Controla as finanças da Mensa Brasil e presta contas à diretoria.'),
    ('DIRETOR.MARKETING', 'Diretor de marketing da Mensa Brasil. Responsável pela divulgação da Mensa Brasil. Cuida da imagem da Mensa Brasil e promove eventos e ações de marketing.'),
    ('SECRETARIO', 'Secretário da Mensa Brasil. Responsável pela documentação da Mensa Brasil. Registra as reuniões e eventos da Mensa Brasil e mantém a documentação atualizada.');

-- Groups table
INSERT INTO iam_groups (group_name, group_description)
VALUES
    ('BETA.TESTER', 'Grupo de testadores beta da Mensa Brasil.'),
    ('SIG.MATEMATICA', 'Grupo de interesse especial em matemática da Mensa Brasil.');

-- Permissions table
INSERT INTO iam_permissions (permission_name, permission_description)
VALUES
    ('CREATE.EVENT', 'Can create events.'),
    ('EDIT.EVENT', 'Can edit events.'),
    ('DELETE.EVENT', 'Can delete events.'),
    ('WHATSAPP.BOT', 'Can interact with the WhatsApp bot.');

-- Role assignments table
INSERT INTO iam_user_roles_map (role_id, registration_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'DIRETOR.REGIONAL'), 5);

INSERT INTO iam_user_roles_map (role_id, registration_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'DIRETOR.MARKETING'), 5);

-- Group assignments table
INSERT INTO iam_user_groups_map (group_id, registration_id)
VALUES
    ((SELECT id FROM iam_groups WHERE group_name = 'BETA.TESTER'), 5);

-- Role permissions table
INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'DIRETOR.REGIONAL'), (SELECT id FROM iam_permissions WHERE permission_name = 'CREATE.EVENT'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
    ((SELECT id FROM iam_roles WHERE role_name = 'DIRETOR.MARKETING'), (SELECT id FROM iam_permissions WHERE permission_name = 'DELETE.EVENT'));

-- Group permissions table
INSERT INTO iam_group_permissions_map (group_id, permission_id)
VALUES
    ((SELECT id FROM iam_groups WHERE group_name = 'BETA.TESTER'), (SELECT id FROM iam_permissions WHERE permission_name = 'WHATSAPP.BOT'));

----- Volunteer activity data
INSERT INTO volunteer_activity_category (name, description, points, id)
VALUES
  ('TEST.CATEGORY', 'A test category for volunteer activities', 1, 10);

INSERT INTO volunteer_activity_log
    (id, registration_id, category_id, title, description, activity_date)
VALUES
    (10, 6, 10, 'Pre-Populated Test Activity', 'This activity log is used for evaluation tests', '2024-10-10'),
    (11, 6, 10, 'Activity 1' , 'This activity log is used for evaluation tests', '2024-10-10');

INSERT INTO iam_permissions (permission_name, permission_description)
VALUES
  ('VOLUNTEER.CATEGORY.CREATE', 'Permission to create volunteer categories'),
  ('VOLUNTEER.CATEGORY.UPDATE', 'Permission to update volunteer categories'),
  ('VOLUNTEER.CATEGORY.DELETE', 'Permission to delete volunteer categories'),
  ('VOLUNTEER.EVALUATION.CREATE', 'Permission to create volunteer evaluations'),
  ('VOLUNTEER.EVALUATION.UPDATE', 'Permission to update volunteer evaluations');

INSERT INTO iam_roles (role_name, role_description)
VALUES ('VOLUNTEER.ADMIN', 'Volunteer administrator with category and evaluation management permissions');

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
  ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'),
   (SELECT id FROM iam_permissions WHERE permission_name = 'VOLUNTEER.CATEGORY.CREATE'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
  ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'),
   (SELECT id FROM iam_permissions WHERE permission_name = 'VOLUNTEER.CATEGORY.UPDATE'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
  ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'),
   (SELECT id FROM iam_permissions WHERE permission_name = 'VOLUNTEER.CATEGORY.DELETE'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
  ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'),
   (SELECT id FROM iam_permissions WHERE permission_name = 'VOLUNTEER.EVALUATION.CREATE'));

INSERT INTO iam_role_permissions_map (role_id, permission_id)
VALUES
  ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'),
   (SELECT id FROM iam_permissions WHERE permission_name = 'VOLUNTEER.EVALUATION.UPDATE'));

INSERT INTO registration
  (registration_id, name, expelled, deceased, transferred, cpf, birth_date, profession, gender, join_date, facebook, created_at, updated_at)

VALUES
  (1805, 'Jessica Diniz Sousa de Santanna', false, false, false, NULL, NULL, NULL, NULL, CURRENT_DATE, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO emails (registration_id, email_address, created_at, updated_at)
VALUES (1805, 'jessica.santanna@mensa.org.br', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO iam_user_roles_map (role_id, registration_id)
VALUES ((SELECT id FROM iam_roles WHERE role_name = 'VOLUNTEER.ADMIN'), 1805);

INSERT INTO iam_groups (group_name, group_description)
VALUES ('VOLUNTEER.MEMBER', 'Group for volunteer members');

INSERT INTO iam_user_groups_map (registration_id, group_id)
SELECT 1805, id
FROM iam_groups
WHERE group_name = 'VOLUNTEER.MEMBER';
