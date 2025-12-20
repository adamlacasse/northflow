DROP DATABASE IF EXISTS northflow;

CREATE DATABASE northflow;
USE northflow;

-- ------------------------------------------------------------------
-- Tables
-- ------------------------------------------------------------------

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE user_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM(
        'text',
        'scale_1_5',
        'number',
        'boolean'
    ) NOT NULL DEFAULT 'text',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_questions_user
    FOREIGN KEY (user_id)
    REFERENCES users (id)
    ON DELETE CASCADE
);

CREATE TABLE checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    CONSTRAINT fk_checkins_user
    FOREIGN KEY (user_id)
    REFERENCES users (id)
    ON DELETE CASCADE
);

CREATE TABLE answers (
    checkin_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text TEXT,
    score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (checkin_id, question_id),
    CONSTRAINT fk_answers_checkin
    FOREIGN KEY (checkin_id)
    REFERENCES checkins (id)
    ON DELETE CASCADE,
    CONSTRAINT fk_answers_question
    FOREIGN KEY (question_id)
    REFERENCES user_questions (id)
    ON DELETE CASCADE
);

-- ------------------------------------------------------------------
-- Seed Data
-- ------------------------------------------------------------------

-- 🌱 Seeders >>>
INSERT INTO users (first_name, last_name, email)
VALUES
('Avery', 'Hart', 'avery.hart@example.com'),
('Jordan', 'Lee', 'jordan.lee@example.com'),
('Quinn', 'Rivera', 'quinn.rivera@example.com'),
('Morgan', 'Blake', 'morgan.blake@example.com'),
('Casey', 'Chen', 'casey.chen@example.com'),
('Taylor', 'Brooks', 'taylor.brooks@example.com'),
('Riley', 'Patel', 'riley.patel@example.com'),
('Alex', 'Santos', 'alex.santos@example.com');

-- Store user IDs in variables for later use
SELECT id INTO @avery_id
FROM users
WHERE email = 'avery.hart@example.com';
SELECT id INTO @jordan_id
FROM users
WHERE email = 'jordan.lee@example.com';
SELECT id INTO @quinn_id
FROM users
WHERE email = 'quinn.rivera@example.com';
SELECT id INTO @morgan_id
FROM users
WHERE email = 'morgan.blake@example.com';
SELECT id INTO @casey_id
FROM users
WHERE email = 'casey.chen@example.com';
SELECT id INTO @taylor_id
FROM users
WHERE email = 'taylor.brooks@example.com';
SELECT id INTO @riley_id
FROM users
WHERE email = 'riley.patel@example.com';
SELECT id INTO @alex_id
FROM users
WHERE email = 'alex.santos@example.com';

INSERT INTO user_questions (
    user_id,
    question_text,
    question_type,
    is_active,
    sort_order
)
VALUES
(@avery_id, 'What are you grateful for today?', 'text', 1, 1),
(@avery_id, 'Rate your stress level (1-5).', 'scale_1_5', 1, 2),

(@jordan_id, 'How many hours did you sleep?', 'number', 1, 1),
(@jordan_id, 'Did you take a mindful break?', 'boolean', 1, 2),

(@quinn_id, 'Describe a win from today.', 'text', 1, 1),
(@quinn_id, 'Rate your energy level (1-5).', 'scale_1_5', 1, 2),

(@morgan_id, 'What made you smile today?', 'text', 1, 1),
(@morgan_id, 'Rate your focus today (1-5).', 'scale_1_5', 1, 2),

(
    @casey_id,
    'How many glasses of water did you drink?',
    'number',
    1,
    1
),
(@casey_id, 'Did you exercise today?', 'boolean', 1, 2),

(@taylor_id, 'What is one thing you learned?', 'text', 1, 1),
(@taylor_id, 'Rate your mood (1-5).', 'scale_1_5', 1, 2),

(
    @riley_id,
    'Describe your biggest challenge today.',
    'text',
    1,
    1
),
(
    @riley_id,
    'Rate your productivity (1-5).',
    'scale_1_5',
    1,
    2
),

(@alex_id, 'What are you looking forward to?', 'text', 1, 1),
(@alex_id, 'Did you practice gratitude?', 'boolean', 1, 2);

INSERT INTO checkins (user_id, checkin_time, notes)
VALUES
(@avery_id, '2024-12-01 08:00:00', 'Morning gratitude session'),
(@avery_id, '2024-12-02 08:15:00', 'Felt more centered after yoga'),
(@jordan_id, '2024-12-01 21:30:00', 'Late-night wind down'),
(@quinn_id, '2024-12-03 07:45:00', 'Quick check before commute'),
(@avery_id, '2024-12-03 08:30:00', 'Good morning reflection'),
(@jordan_id, '2024-12-02 22:00:00', 'Evening wrap-up'),
(@quinn_id, '2024-12-04 09:00:00', 'Mid-week check-in'),
(@morgan_id, '2024-12-01 07:00:00', 'Early bird session'),
(@morgan_id, '2024-12-02 19:30:00', 'Evening mindfulness'),
(@casey_id, '2024-12-01 12:00:00', 'Lunch break reflection'),
(@casey_id, '2024-12-03 11:45:00', 'Midday pause'),
(@taylor_id, '2024-12-02 08:00:00', 'Morning routine'),
(@taylor_id, '2024-12-04 08:15:00', 'Fresh start'),
(@riley_id, '2024-12-01 18:00:00', 'End of day review'),
(@riley_id, '2024-12-03 17:45:00', 'Afternoon reflection'),
(@alex_id, '2024-12-02 07:30:00', 'Dawn check-in'),
(@alex_id, '2024-12-04 20:00:00', 'Night-time gratitude'),
(@avery_id, '2024-12-05 08:00:00', 'Friday morning check'),
(@quinn_id, '2024-12-05 10:30:00', 'Mid-morning energy boost'),
(@morgan_id, '2024-12-03 14:00:00', 'Afternoon focus session'),
(@taylor_id, '2024-12-05 07:45:00', 'Early Friday reflection'),
(@riley_id, '2024-12-04 20:30:00', 'Evening productivity review');

-- Store checkin IDs in variables for later use
SELECT id INTO @checkin1
FROM checkins
WHERE notes = 'Morning gratitude session';
SELECT id INTO @checkin2
FROM checkins
WHERE notes = 'Felt more centered after yoga';
SELECT id INTO @checkin3
FROM checkins
WHERE notes = 'Late-night wind down';
SELECT id INTO @checkin4
FROM checkins
WHERE notes = 'Quick check before commute';

-- Store additional checkin IDs
SELECT id INTO @checkin5
FROM checkins
WHERE notes = 'Good morning reflection';
SELECT id INTO @checkin6
FROM checkins
WHERE notes = 'Evening wrap-up';
SELECT id INTO @checkin7
FROM checkins
WHERE notes = 'Mid-week check-in';
SELECT id INTO @checkin8
FROM checkins
WHERE notes = 'Early bird session';
SELECT id INTO @checkin9
FROM checkins
WHERE notes = 'Evening mindfulness';
SELECT id INTO @checkin10
FROM checkins
WHERE notes = 'Lunch break reflection';
SELECT id INTO @checkin11
FROM checkins
WHERE notes = 'Midday pause';
SELECT id INTO @checkin12
FROM checkins
WHERE notes = 'Morning routine';
SELECT id INTO @checkin13
FROM checkins
WHERE notes = 'Fresh start';
SELECT id INTO @checkin14
FROM checkins
WHERE notes = 'End of day review';
SELECT id INTO @checkin15
FROM checkins
WHERE notes = 'Afternoon reflection';
SELECT id INTO @checkin16
FROM checkins
WHERE notes = 'Dawn check-in';
SELECT id INTO @checkin17
FROM checkins
WHERE notes = 'Night-time gratitude';
SELECT id INTO @checkin18
FROM checkins
WHERE notes = 'Friday morning check';
SELECT id INTO @checkin19
FROM checkins
WHERE notes = 'Mid-morning energy boost';
SELECT id INTO @checkin20
FROM checkins
WHERE notes = 'Afternoon focus session';
SELECT id INTO @checkin21
FROM checkins
WHERE notes = 'Early Friday reflection';
SELECT id INTO @checkin22
FROM checkins
WHERE notes = 'Evening productivity review';

INSERT INTO answers (checkin_id, question_id, answer_text, score)
VALUES
-- Avery's answers
(
    @checkin1,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'What are you grateful%'
    ),
    'Sunrise walk with coffee',
    NULL
),
(
    @checkin1,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'Rate your stress%'
    ),
    NULL,
    4.00
),
(
    @checkin2,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'What are you grateful%'
    ),
    'Supportive chat with a friend',
    NULL
),
(
    @checkin2,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'Rate your stress%'
    ),
    NULL,
    3.00
),
(
    @checkin5,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'What are you grateful%'
    ),
    'Beautiful weather',
    NULL
),
(
    @checkin5,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'Rate your stress%'
    ),
    NULL,
    2.00
),
(
    @checkin18,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'What are you grateful%'
    ),
    'Productive week coming to close',
    NULL
),
(
    @checkin18,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @avery_id
            AND question_text LIKE 'Rate your stress%'
    ),
    NULL,
    2.00
),

-- Jordan's answers
(
    @checkin3,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @jordan_id
            AND question_text LIKE 'How many hours%'
    ),
    '7',
    NULL
),
(
    @checkin3,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @jordan_id
            AND question_text LIKE 'Did you take%'
    ),
    '1',
    NULL
),
(
    @checkin6,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @jordan_id
            AND question_text LIKE 'How many hours%'
    ),
    '8',
    NULL
),
(
    @checkin6,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @jordan_id
            AND question_text LIKE 'Did you take%'
    ),
    '1',
    NULL
),

-- Quinn's answers with scale_1_5
(
    @checkin4,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Describe a win%'
    ),
    'Completed project milestone',
    NULL
),
(
    @checkin4,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Rate your energy%'
    ),
    NULL,
    4.00
),
(
    @checkin7,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Describe a win%'
    ),
    'Helped a colleague solve a bug',
    NULL
),
(
    @checkin7,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Rate your energy%'
    ),
    NULL,
    5.00
),
(
    @checkin19,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Describe a win%'
    ),
    'Received positive feedback',
    NULL
),
(
    @checkin19,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @quinn_id
            AND question_text LIKE 'Rate your energy%'
    ),
    NULL,
    5.00
),

-- Morgan's answers with scale_1_5
(
    @checkin8,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'What made you smile%'
    ),
    'Kids playing in the park',
    NULL
),
(
    @checkin8,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'Rate your focus%'
    ),
    NULL,
    3.00
),
(
    @checkin9,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'What made you smile%'
    ),
    'Finished a good book',
    NULL
),
(
    @checkin9,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'Rate your focus%'
    ),
    NULL,
    4.00
),
(
    @checkin20,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'What made you smile%'
    ),
    'Great conversation over lunch',
    NULL
),
(
    @checkin20,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @morgan_id
            AND question_text LIKE 'Rate your focus%'
    ),
    NULL,
    5.00
),

-- Casey's answers
(
    @checkin10,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @casey_id
            AND question_text LIKE 'How many glasses%'
    ),
    '6',
    NULL
),
(
    @checkin10,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @casey_id
            AND question_text LIKE 'Did you exercise%'
    ),
    '0',
    NULL
),
(
    @checkin11,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @casey_id
            AND question_text LIKE 'How many glasses%'
    ),
    '8',
    NULL
),
(
    @checkin11,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @casey_id
            AND question_text LIKE 'Did you exercise%'
    ),
    '1',
    NULL
),

-- Taylor's answers with scale_1_5
(
    @checkin12,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'What is one thing%'
    ),
    'New debugging technique',
    NULL
),
(
    @checkin12,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'Rate your mood%'
    ),
    NULL,
    4.00
),
(
    @checkin13,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'What is one thing%'
    ),
    'Team collaboration strategy',
    NULL
),
(
    @checkin13,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'Rate your mood%'
    ),
    NULL,
    5.00
),
(
    @checkin21,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'What is one thing%'
    ),
    'Code optimization patterns',
    NULL
),
(
    @checkin21,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @taylor_id
            AND question_text LIKE 'Rate your mood%'
    ),
    NULL,
    4.00
),

-- Riley's answers with scale_1_5
(
    @checkin14,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Describe your biggest%'
    ),
    'Time management issues',
    NULL
),
(
    @checkin14,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Rate your productivity%'
    ),
    NULL,
    3.00
),
(
    @checkin15,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Describe your biggest%'
    ),
    'Complex code refactoring',
    NULL
),
(
    @checkin15,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Rate your productivity%'
    ),
    NULL,
    4.00
),
(
    @checkin22,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Describe your biggest%'
    ),
    'Meeting coordination across timezones',
    NULL
),
(
    @checkin22,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @riley_id
            AND question_text LIKE 'Rate your productivity%'
    ),
    NULL,
    5.00
),

-- Alex's answers
(
    @checkin16,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @alex_id
            AND question_text LIKE 'What are you looking%'
    ),
    'Weekend hiking trip',
    NULL
),
(
    @checkin16,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @alex_id
            AND question_text LIKE 'Did you practice%'
    ),
    '1',
    NULL
),
(
    @checkin17,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @alex_id
            AND question_text LIKE 'What are you looking%'
    ),
    'Upcoming team celebration',
    NULL
),
(
    @checkin17,
    (
        SELECT id
        FROM user_questions
        WHERE
            user_id = @alex_id
            AND question_text LIKE 'Did you practice%'
    ),
    '1',
    NULL
);

-- ------------------------------------------------------------------
-- Views / Procedures
-- ------------------------------------------------------------------

CREATE VIEW user_daily_summary AS
SELECT
    u.id AS user_id,
    u.first_name,
    u.last_name,
    DATE(c.checkin_time) AS checkin_date,
    COUNT(DISTINCT c.id) AS total_checkins,
    COUNT(a.question_id) AS total_answers,
    AVG(a.score) AS avg_score,
    MIN(a.score) AS min_score,
    MAX(a.score) AS max_score
FROM users AS u
LEFT JOIN checkins AS c
    ON u.id = c.user_id
LEFT JOIN answers AS a
    ON c.id = a.checkin_id
GROUP BY
    u.id,
    u.first_name,
    u.last_name,
    DATE(c.checkin_time)
ORDER BY
    checkin_date DESC;

-- noqa: disable=PRS
DELIMITER $$

CREATE PROCEDURE health_check ()
BEGIN
    SELECT 1 AS status;
END$$

CREATE PROCEDURE list_users ()
BEGIN
    SELECT
        id,
        first_name,
        last_name,
        email
    FROM users
    ORDER BY last_name, first_name;
END$$

CREATE PROCEDURE list_user_questions ()
BEGIN
    SELECT
        uq.id,
        uq.user_id,
        CONCAT(u.first_name, ' ', u.last_name) AS user_name,
        uq.question_text,
        uq.question_type,
        uq.is_active,
        uq.sort_order
    FROM user_questions AS uq
    JOIN users AS u ON u.id = uq.user_id
    ORDER BY u.last_name, u.first_name, uq.sort_order, uq.id;
END$$

CREATE PROCEDURE list_daily_summary (
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT
        user_id,
        CONCAT(first_name, ' ', last_name) AS user_name,
        checkin_date,
        total_checkins,
        total_answers,
        avg_score,
        min_score,
        max_score
    FROM user_daily_summary
    WHERE
        (p_user_id IS NULL OR user_id = p_user_id)
        AND (p_start_date IS NULL OR checkin_date >= p_start_date)
        AND (p_end_date IS NULL OR checkin_date <= p_end_date)
    ORDER BY checkin_date DESC, user_name ASC;
END$$

CREATE PROCEDURE add_user_question (
    IN p_user_id INT,
    IN p_question_text TEXT,
    IN p_question_type VARCHAR(20),
    IN p_is_active TINYINT(1),
    IN p_sort_order INT
)
BEGIN
    IF p_question_type NOT IN (
        'text',
        'scale_1_5',
        'number',
        'boolean'
    ) THEN
        SET @error_msg = CONCAT('Invalid question_type: ', p_question_type);
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = @error_msg;
    END IF;

    INSERT INTO user_questions (
        user_id,
        question_text,
        question_type,
        is_active,
        sort_order
    )
    VALUES (
        p_user_id,
        p_question_text,
        p_question_type,
        p_is_active,
        p_sort_order
    );
END$$

CREATE PROCEDURE update_user_question (
    IN p_question_id INT,
    IN p_question_text TEXT,
    IN p_question_type VARCHAR(20),
    IN p_is_active TINYINT(1),
    IN p_sort_order INT,
    OUT p_success TINYINT(1)
)
BEGIN
    IF p_question_type NOT IN (
        'text',
        'scale_1_5',
        'number',
        'boolean'
    ) THEN
        SET @error_msg = CONCAT('Invalid question_type: ', p_question_type);
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = @error_msg;
    END IF;

    UPDATE user_questions
    SET
        question_text = p_question_text,
        question_type = p_question_type,
        is_active = p_is_active,
        sort_order = p_sort_order
    WHERE id = p_question_id;

    SET p_success = (ROW_COUNT() > 0);
END$$

CREATE PROCEDURE delete_user_question (
    IN p_question_id INT
)
BEGIN
    DELETE FROM user_questions
    WHERE id = p_question_id;
END$$

DELIMITER ; -- noqa: disable=PRS
-- noqa: enable=PRS
