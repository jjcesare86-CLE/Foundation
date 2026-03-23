-- Foundation Schema Setup
-- Run this first in the Supabase SQL Editor

-- Enable pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create foundation schema
CREATE SCHEMA IF NOT EXISTS foundation;
