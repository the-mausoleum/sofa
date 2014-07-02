drop table if exists shows;
create table shows (
    id integer primary key autoincrement,
    show_id text not null,
    title text not null,
    seasons integer not null,
    description text
);

drop table if exists seasons;
create table seasons (
    id integer primary key autoincrement,
    season_id integer not null,
    episodes integer not null
);

drop table if exists episodes;
create table episodes (
    id integer primary key autoincrement,
    episode_id integer not null,
    title text not null
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    email text not null,
    username text not null,
    password text not null,
    first_name text not null,
    last_name text not null,
    permissions integer not null
);