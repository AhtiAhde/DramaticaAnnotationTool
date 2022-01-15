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

CREATE TYPE annotool.dramatica_plot_point AS ENUM ('goal', 'requirements', 'consequences', 'forewarnings', 'dividends', 'costs', 'prerequisites', 'preconditions')
CREATE TYPE annotool.mice_type AS ENUM ('mileau', 'inquiry', 'character', 'event');
CREATE TYPE annotool.ppp_phase AS ENUM ('promise', 'progress', 'payoff');
CREATE TYPE annotool.aux_type AS ENUM ('nothing', 'dialogue', 'nic', 'ic', 'event', 'undef_arc', 'bug');

CREATE TABLE annotool.annotation_arc (id SERIAL PRIMARY KEY, book_id INTEGER, user_id UUID, title TEXT, short_desc TEXT);
CREATE TABLE annotool.meta_aux (id SERIAL PRIMARY KEY, user_id UUID, paragraph_id INTEGER, aux_type annotool.aux_type);
CREATE TABLE annotool.meta_dramatica_element (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, element TEXT);
CREATE TABLE annotool.meta_dramatica_pp (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, pp annotool.dramatica_plot_point, theme TEXT);
CREATE TABLE annotool.meta_mice (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, mice_type annotool.mice_type, annotation_note TEXT, is_start_event BOOLEAN);
CREATE TABLE annotool.meta_ppp (id SERIAL PRIMARY KEY, arc_id INTEGER, paragraph_id INTEGER, phase annotool.ppp_phase, promise_id INTEGER);
