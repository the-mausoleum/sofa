drop table if exists shows;
create table shows (
    id integer primary key autoincrement,
    public_id text not null,
    title text not null,
    seasons integer not null,
    description text
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null
);