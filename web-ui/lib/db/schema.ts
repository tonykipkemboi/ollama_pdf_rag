import type { InferSelectModel } from "drizzle-orm";
import {
  integer,
  sqliteTable,
  text,
} from "drizzle-orm/sqlite-core";

// Simplified schema for local development without authentication
export const chat = sqliteTable("chat", {
  id: text("id").notNull().primaryKey(),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
  title: text("title").notNull(),
  visibility: text("visibility").default("private"),
  userId: text("user_id").notNull().default("local-user"),
});

export type Chat = InferSelectModel<typeof chat>;

export const message = sqliteTable("message", {
  id: text("id").notNull().primaryKey(),
  chatId: text("chat_id")
    .notNull()
    .references(() => chat.id),
  role: text("role").notNull(),
  content: text("content").notNull(),
  sources: text("sources"), // JSON string for source info
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});

export type Message = InferSelectModel<typeof message>;
export type DBMessage = Message;

// Stub tables for compatibility with Vercel AI chatbot queries
export const user = sqliteTable("user", {
  id: text("id").notNull().primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text("email").notNull(),
  password: text("password"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});

export type User = InferSelectModel<typeof user>;

export const document = sqliteTable("document", {
  id: text("id").notNull().primaryKey().$defaultFn(() => crypto.randomUUID()),
  title: text("title").notNull(),
  content: text("content"),
  kind: text("kind"),
  userId: text("user_id")
    .notNull()
    .references(() => user.id),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});

export type Document = InferSelectModel<typeof document>;

export const suggestion = sqliteTable("suggestion", {
  id: text("id").notNull().primaryKey().$defaultFn(() => crypto.randomUUID()),
  documentId: text("document_id")
    .notNull()
    .references(() => document.id),
  documentCreatedAt: integer("document_created_at", { mode: "timestamp" }),
  content: text("content").notNull(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});

export type Suggestion = InferSelectModel<typeof suggestion>;

export const vote = sqliteTable("vote", {
  chatId: text("chat_id")
    .notNull()
    .references(() => chat.id),
  messageId: text("message_id").notNull(),
  isUpvoted: integer("is_upvoted", { mode: "boolean" }).notNull(),
});

export type Vote = InferSelectModel<typeof vote>;

export const stream = sqliteTable("stream", {
  id: text("id").notNull().primaryKey().$defaultFn(() => crypto.randomUUID()),
  chatId: text("chat_id")
    .notNull()
    .references(() => chat.id),
  content: text("content").notNull().default(""),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});

export type Stream = InferSelectModel<typeof stream>;
