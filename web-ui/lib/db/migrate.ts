import { config } from "dotenv";
import { drizzle } from "drizzle-orm/better-sqlite3";
import { migrate } from "drizzle-orm/better-sqlite3/migrator";
import Database from "better-sqlite3";
import { join } from "path";
import { mkdirSync } from "fs";

config({
  path: ".env.local",
});

const runMigrate = async () => {
  // Ensure data directory exists
  const dataDir = join(process.cwd(), "data");
  try {
    mkdirSync(dataDir, { recursive: true });
  } catch {
    // Directory may already exist
  }

  const dbPath = join(dataDir, "chat.db");
  console.log(`📁 Using SQLite database at: ${dbPath}`);

  const sqlite = new Database(dbPath);
  const db = drizzle(sqlite);

  console.log("⏳ Running migrations...");

  const start = Date.now();
  try {
    migrate(db, { migrationsFolder: "./lib/db/migrations" });
  } catch (err: any) {
    // Ignore "already exists" errors for SQLite
    if (!err.message?.includes("already exists")) {
      throw err;
    }
    console.log("⚠️ Some tables already exist, skipping...");
  }
  const end = Date.now();

  console.log("✅ Migrations completed in", end - start, "ms");

  sqlite.close();
  process.exit(0);
};

runMigrate().catch((err) => {
  console.error("❌ Migration failed");
  console.error(err);
  process.exit(1);
});
