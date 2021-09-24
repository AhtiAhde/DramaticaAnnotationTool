-- As super user
CREATE SCHEMA annotool;
GRANT ALL ON SCHEMA annotool TO user;
GRANT ALL ON ALL TABLES IN SCHEMA annotool TO user;

-- As user
CREATE TABLE annotool.books (id SERIAL PRIMARY KEY, title TEXT, origin TEXT UNIQUE);
CREATE TABLE annotool.paragraphs (id SERIAL PRIMARY KEY, book_id INTEGER, seq_num INTEGER, content TEXT);
CREATE TABLE annotool.users (id UUID PRIMARY KEY, email TEXT UNIQUE, pwd TEXT);
CREATE TABLE annotool.characters (id SERIAL PRIMARY KEY, book_id INTEGER NOT NULL, name TEXT NOT NULL);
CREATE TABLE annotool.role_annotations (id SERIAL PRIMARY KEY, user_id UUID NOT NULL, char_id INTEGER NULL, role TEXT NOT NULL);
