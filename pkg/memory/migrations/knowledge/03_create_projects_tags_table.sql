CREATE TABLE IF NOT EXISTS project_tags (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
