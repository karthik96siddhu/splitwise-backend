# splitwise-backend

### whenever you change your models
- Run alembic revision --autogenerate -m "describe change"
- run alembic upgrade head
- to revert back to previous version run "alembic downgrade -1"
- to revert to specific version find a down_revision variable and copy the value then run "alembic downgrade VERSION"
-  if you want to empty tables run "alembic downgrade base"
- NOTE models don't rollback automatically. We have to change manually in models files. 
- "Migration file controls DB, not code!"

### If you want to clear db and versions follow below command
- alembic revision --autogenerate -m "Initial tables setup"
- alembic upgrade head
