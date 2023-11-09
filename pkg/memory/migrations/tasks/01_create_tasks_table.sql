CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queueID TEXT NOT NULL,
    taskData TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('in-progress', 'failed', 'done', 'queued')),
    result TEXT,
    systemMessage TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}',
    parent TEXT,
    children TEXT DEFAULT '[]'
);
