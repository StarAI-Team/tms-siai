CREATE TABLE IF NOT EXISTS client (
                    user_id TEXT PRIMARY KEY,
                    company_email TEXT UNIQUE NOT NULL,
                    company_location TEXT UNIQUE NOT NULL,
                    company_name TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    id_number TEXT UNIQUE NOT NULL,
                    last_name TEXT NOT NULL,
                    phone_number TEXT UNIQUE NOT NULL,
                    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );