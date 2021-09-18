-- As super user
CREATE SCHEMA annotool;
GRANT ALL ON SCHEMA annotool TO user;
GRANT ALL ON ALL TABLES IN SCHEMA annotool TO user;

-- As user
CREATE TABLE annotool.books (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO annotool.books (name) VALUES ('Test Book');
CREATE TABLE annotool.users (id UUID PRIMARY KEY, email TEXT UNIQUE, pwd TEXT);