-- Migration: Add chat_pdf table for document separation per chat
-- Also update message table to use parts instead of content/sources

-- Create chat_pdf table to link PDFs to specific chats
CREATE TABLE IF NOT EXISTS `chat_pdf` (
	`chat_id` text NOT NULL,
	`pdf_id` text NOT NULL,
	`added_at` integer NOT NULL DEFAULT (unixepoch()),
	FOREIGN KEY (`chat_id`) REFERENCES `chat`(`id`) ON UPDATE no action ON DELETE no action
);

-- Add parts column to message table if it doesn't exist
-- SQLite doesn't support IF NOT EXISTS for columns, so we handle this in code
