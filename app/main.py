from fastapi import FastAPI
from app.api.intake_api import inta
from app.db.db_config import engine
from app.db.models import Base
from app.api.enter_docter_pres import enter_docter
from app.helper.schedular import scheduler

app = FastAPI()
app.include_router(inta)
app.include_router(enter_docter)



@app.on_event("startup")
def startup_event():
   Base.metadata.create_all(bind=engine)
   if not scheduler.running:
        scheduler.start()
