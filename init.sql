DO
$$
BEGIN
   CREATE ROLE releasebot WITH LOGIN PASSWORD 'releasebot';
EXCEPTION
   WHEN duplicate_object THEN null;
END
$$;

-- Create the types we need
DO $$ BEGIN
    CREATE TYPE release_status AS ENUM ('processing', 'completed', 'failed');
    CREATE TYPE user_status AS ENUM ('active', 'inactive');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

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
    status user_status DEFAULT 'active',
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