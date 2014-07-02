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
    season_id number not null,
    episodes integer not null
);

drop table if exists episodes;
create table episodes (
    id integer primary key autoincrement,
    episode_id number not null,
    title text not null
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null
);