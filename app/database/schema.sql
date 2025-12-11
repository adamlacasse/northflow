DROP DATABASE IF EXISTS northflow;

CREATE DATABASE northflow;
USE northflow;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE user_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM(
        'text', 'scale_1_5', 'number', 'boolean'
    ) NOT NULL DEFAULT 'text',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

-- Views/procedures/functions >>>

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
