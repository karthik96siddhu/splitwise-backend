# splitwise-backend

### whenever you change your models

- Run alembic revision --autogenerate -m "describe change"
- run alembic upgrade head
- to revert back to previous version run "alembic downgrade -1"
- to revert to specific version find a down_revision variable and copy the value then run "alembic downgrade VERSION"
- if you want to empty tables run "alembic downgrade base"
- NOTE models don't rollback automatically. We have to change manually in models files.
- "Migration file controls DB, not code!"

### If you want to clear db and versions follow below command

- alembic revision --autogenerate -m "Initial tables setup"
- alembic upgrade head

### to resolve migration issues

- If you added new column to table and without saving the file you ran alembic revision command. It will create empty new version then you tried to save again and delete the latest version manually. Again you repeat the process you will get into trouble. To resolve those follow below steps.
- Find out history of version - alembic history --verbose
- Check current alembic version db pointing to - alembic current. You will find version will be behind your current version files.
- Now re-set alembic head to point to latest version you have in your local code - alembic stamp head. Then you can proceed with updating the column to the table from beginning.
