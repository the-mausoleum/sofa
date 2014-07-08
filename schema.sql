drop table if exists shows;
create table shows (
    id integer primary key autoincrement,
    public_id text not null,
    title text,
    season_count integer,
    description text
);

drop table if exists seasons;
create table seasons (
    id integer primary key autoincrement,
    public_id integer not null,
    episode_count integer
);

drop table if exists episodes;
create table episodes (
    id integer primary key autoincrement,
    public_id integer not null,
    title text,
    show integer,
    season integer
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    email text not null,
    username text not null,
    password text not null,
    first_name text,
    last_name text,
    permissions integer not null
);

drop table if exists watch_history;
create table watch_history (
    id integer primary key autoincrement,
    user_id integer,
    episode_id integer
);