-- As super user

-- As user
CREATE TABLE books (id SERIAL PRIMARY KEY, title TEXT, origin TEXT UNIQUE);
CREATE TABLE paragraphs (id SERIAL PRIMARY KEY, book_id INTEGER, seq_num INTEGER, content TEXT);
CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT);
CREATE TABLE user_sessions (id UUID PRIMARY KEY, owner TEXT);
CREATE TABLE characters (id SERIAL PRIMARY KEY, book_id INTEGER NOT NULL, name TEXT NOT NULL);
CREATE TABLE role_annotations (id SERIAL PRIMARY KEY, session_id UUID NOT NULL, char_id INTEGER NULL, role TEXT NOT NULL);

CREATE TYPE dramatica_plot_point AS ENUM ('unknown', 'goal', 'requirements', 'consequences', 'forewarnings', 'dividends', 'costs', 'prerequisites', 'preconditions');
CREATE TYPE dramatica_pp_theme AS ENUM('unknown', 'past', 'progress', 'future', 'present', 'understanding', 'doing', 'obtaining', 'learning', 'conceptualization', 'being', 'becoming', 'conceiving', 'memory', 'preconscious', 'subconsciouse', 'conscious');
CREATE TYPE mice_type AS ENUM ('mileau', 'inquiry', 'character', 'event');
CREATE TYPE ppp_phase AS ENUM ('promise', 'progress', 'payoff');
CREATE TYPE aux_type AS ENUM ('nothing', 'dialogue', 'nic', 'ic', 'event', 'undef_arc', 'bug');

CREATE TABLE annotation_arc (id SERIAL PRIMARY KEY, book_id INTEGER, session_id UUID, title TEXT, short_desc TEXT);
CREATE TABLE meta_aux (id SERIAL PRIMARY KEY, session_id UUID, paragraph_id INTEGER, aux_type aux_type);
CREATE TABLE meta_dramatica_element (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, element TEXT);
CREATE TABLE meta_dramatica_pp (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, plot_point dramatica_plot_point, theme dramatica_pp_theme, annotation_note TEXT);
CREATE TABLE meta_mice (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, mice_type mice_type, annotation_note TEXT, is_start_event BOOLEAN);
CREATE TABLE meta_ppp (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, phase ppp_phase, annotation_note TEXT);
