-- Таблица для хранения групп файлов
CREATE TABLE file_groups (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(255) UNIQUE NOT NULL
);

-- Таблица для хранения информации о файлах
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES file_groups(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    timestamp TIMESTAMP,
    content BYTEA
);


CREATE TABLE chats (
    id UUID PRIMARY KEY,
    name VARCHAR(255)
);

-- Таблица для хранения истории чата
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(50),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chat_id UUID REFERENCES chats(id)
);
