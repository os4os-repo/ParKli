docker exec -i parkli-postgres pg_restore --verbose --clean --no-acl --no-owner -h <HOST> -U <USER> -d <DATABASE> < ./host-volumes/dbdump/sicherungsdatei.dump
