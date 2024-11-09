FROM postgres:16.4

COPY db.sql /docker-entrypoint-initdb.d

EXPOSE 5432
