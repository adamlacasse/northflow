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
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_oauth (oauth_provider, oauth_id)
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
-- ------------------------------------------------------------------
-- Seed Data
-- ------------------------------------------------------------------

-- Optional demo user for local development/testing.
-- OAuth users are normally auto-registered at first login.
-- Do not use this demo account pattern in production.
-- Note: oauth_provider and oauth_id are intentionally NULL for this local-only user.
INSERT INTO users (first_name, last_name, email, oauth_provider, oauth_id)
VALUES ('Demo', 'User', 'demo@northflow.app', NULL, NULL);

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
    IN p_user_id INT,
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
    WHERE id = p_question_id AND user_id = p_user_id;

    SET p_success = (ROW_COUNT() > 0);
END$$

CREATE PROCEDURE delete_user_question (
    IN p_question_id INT,
    IN p_user_id INT
)
BEGIN
    DELETE FROM user_questions
    WHERE id = p_question_id AND user_id = p_user_id;
END$$

CREATE PROCEDURE add_checkin (
    IN p_user_id INT,
    IN p_notes TEXT
)
BEGIN
    INSERT INTO checkins (user_id, notes)
    VALUES (p_user_id, p_notes);
    SELECT LAST_INSERT_ID() AS checkin_id;
END$$

CREATE PROCEDURE update_checkin (
    IN p_checkin_id INT,
    IN p_user_id INT,
    IN p_notes TEXT,
    OUT p_success TINYINT(1)
)
BEGIN
    UPDATE checkins
    SET notes = p_notes
    WHERE id = p_checkin_id AND user_id = p_user_id;

    SET p_success = (ROW_COUNT() > 0);
END$$

CREATE PROCEDURE delete_checkin (
    IN p_checkin_id INT,
    IN p_user_id INT
)
BEGIN
    DELETE FROM checkins
    WHERE id = p_checkin_id AND user_id = p_user_id;
END$$

CREATE PROCEDURE get_checkin (
    IN p_checkin_id INT,
    IN p_user_id INT
)
BEGIN
    SELECT
        c.id,
        c.user_id,
        CONCAT(u.first_name, ' ', u.last_name) AS user_name,
        c.checkin_time,
        c.notes
    FROM checkins AS c
    JOIN users AS u ON u.id = c.user_id
    WHERE c.id = p_checkin_id AND c.user_id = p_user_id;
END$$

CREATE PROCEDURE list_checkins (
    IN p_user_id INT
)
BEGIN
    SELECT
        c.id,
        c.user_id,
        CONCAT(u.first_name, ' ', u.last_name) AS user_name,
        c.checkin_time,
        c.notes,
        COUNT(a.question_id) AS answer_count
    FROM checkins AS c
    JOIN users AS u ON u.id = c.user_id
    LEFT JOIN answers AS a ON a.checkin_id = c.id
    WHERE c.user_id = p_user_id
    GROUP BY c.id
    ORDER BY c.checkin_time DESC;
END$$

CREATE PROCEDURE add_answer (
    IN p_checkin_id INT,
    IN p_question_id INT,
    IN p_answer_text TEXT,
    IN p_score DECIMAL(5, 2)
)
BEGIN
    INSERT INTO answers (
        checkin_id,
        question_id,
        answer_text,
        score
    )
    VALUES (
        p_checkin_id,
        p_question_id,
        p_answer_text,
        p_score
    )
    ON DUPLICATE KEY UPDATE
        answer_text = p_answer_text,
        score = p_score;
END$$

CREATE PROCEDURE update_answer (
    IN p_checkin_id INT,
    IN p_question_id INT,
    IN p_answer_text TEXT,
    IN p_score DECIMAL(5, 2),
    OUT p_success TINYINT(1)
)
BEGIN
    UPDATE answers
    SET
        answer_text = p_answer_text,
        score = p_score
    WHERE
        checkin_id = p_checkin_id
        AND question_id = p_question_id;

    SET p_success = (ROW_COUNT() > 0);
END$$

CREATE PROCEDURE delete_answer (
    IN p_checkin_id INT,
    IN p_question_id INT
)
BEGIN
    DELETE FROM answers
    WHERE
        checkin_id = p_checkin_id
        AND question_id = p_question_id;
END$$

CREATE PROCEDURE get_checkin_answers (
    IN p_checkin_id INT
)
BEGIN
    SELECT
        a.checkin_id,
        a.question_id,
        uq.question_text,
        uq.question_type,
        a.answer_text,
        a.score
    FROM answers AS a
    JOIN user_questions AS uq ON uq.id = a.question_id
    WHERE a.checkin_id = p_checkin_id
    ORDER BY uq.sort_order, uq.id;
END$$

DELIMITER ; -- noqa: disable=PRS
-- noqa: enable=PRS
