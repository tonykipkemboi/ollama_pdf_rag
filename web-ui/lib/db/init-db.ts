import Database from "better-sqlite3";
import { join } from "path";

const dbPath = join(process.cwd(), "data", "chat.db");
const db = new Database(dbPath);

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    email TEXT NOT NULL UNIQUE,
    password TEXT,
    created_at INTEGER NOT NULL DEFAULT (unixepoch())
  );

  CREATE TABLE IF NOT EXISTS chat (
    id TEXT PRIMARY KEY,
    created_at INTEGER NOT NULL,
    title TEXT NOT NULL,
    user_id TEXT NOT NULL DEFAULT 'local-user',
    visibility TEXT DEFAULT 'private',
    FOREIGN KEY (user_id) REFERENCES user(id)
  );

  CREATE TABLE IF NOT EXISTS message (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    parts TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chat(id)
  );

  CREATE TABLE IF NOT EXISTS chat_pdf (
    chat_id TEXT NOT NULL,
    pdf_id TEXT NOT NULL,
    added_at INTEGER NOT NULL DEFAULT (unixepoch()),
    PRIMARY KEY (chat_id, pdf_id),
    FOREIGN KEY (chat_id) REFERENCES chat(id)
  );

  CREATE TABLE IF NOT EXISTS document (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    user_id TEXT NOT NULL,
    kind TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
  );

  CREATE TABLE IF NOT EXISTS suggestion (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id TEXT NOT NULL,
    document_created_at INTEGER,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (document_id) REFERENCES document(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
  );

  CREATE TABLE IF NOT EXISTS vote (
    chat_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    is_upvoted INTEGER NOT NULL,
    PRIMARY KEY (chat_id, message_id),
    FOREIGN KEY (chat_id) REFERENCES chat(id)
  );

  CREATE TABLE IF NOT EXISTS stream (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chat(id)
  );
`);

console.log("Database initialized successfully!");
db.close();
