drop table if exists shows;
create table shows (
    id integer primary key autoincrement,
    title text not null,
    seasons integer not null
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null
);