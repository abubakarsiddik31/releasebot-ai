DO
$$
BEGIN
    CREATE ROLE releasebot WITH LOGIN PASSWORD 'releasebot';
EXCEPTION
    WHEN duplicate_object THEN null;
END
$$;

-- Drop existing enum types if they exist
DO $$ 
BEGIN
    DROP TYPE IF EXISTS release_status CASCADE;
    DROP TYPE IF EXISTS user_status CASCADE;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Could not drop enum types: %', SQLERRM;
END $$;

-- Create the types we need
CREATE TYPE release_status AS ENUM ('processing', 'completed', 'failed');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'bounced', 'unsubscribed');

CREATE TABLE IF NOT EXISTS releases_processed (
    id SERIAL PRIMARY KEY,
    release_tag VARCHAR(50) UNIQUE NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status release_status DEFAULT 'processing',
    brevo_campaign_id VARCHAR(100),
    email_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_content (
    id SERIAL PRIMARY KEY,
    release_tag VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (release_tag) REFERENCES releases_processed(release_tag)
);

-- Grant all privileges to the releasebot user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO releasebot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO releasebot;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO releasebot;