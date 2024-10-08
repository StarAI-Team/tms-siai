CREATE TABLE IF NOT EXISTS transporter (
    user_id TEXT PRIMARY KEY,
    company_email TEXT UNIQUE NOT NULL,
    company_location TEXT NOT NULL,
    company_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transporter_account_information (
    user_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    bank_name TEXT NOT NULL,
    company_contact TEXT NOT NULL,
    directorship TEXT NOT NULL,
    proof_of_current_address TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES transporter(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transporter_documentation (
    user_id TEXT PRIMARY KEY,
    certificate_of_incorporation TEXT NOT NULL,
    operators_expiry DATE NOT NULL,
    operators_licence TEXT NOT NULL,
    permit_expiry DATE NOT NULL,
    permits TEXT NOT NULL,
    permits_text TEXT NOT NULL,
    tax_clearance TEXT NOT NULL,
    tax_expiry DATE NOT NULL,
    tracking_licence TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES transporter(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transporter_fleet (
    user_id TEXT PRIMARY KEY,
    certificate_of_fitness TEXT NOT NULL,
    num_of_trucks TEXT NOT NULL,
    number_of_trucks INT NOT NULL,
    reg_books TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES transporter(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transporter_profile (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    profile_picture TEXT NOT NULL,
    password TEXT NOT NULL,
    confirm_password TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES transporter(user_id) ON DELETE CASCADE
);




