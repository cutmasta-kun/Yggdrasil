CREATE TABLE IF NOT EXISTS speech_bubbles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(100) NOT NULL CHECK(role IN ('system', 'assistant', 'user', 'function')),
    content TEXT NOT NULL,
    name TEXT DEFAULT NULL,
    function_call TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}',

    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
