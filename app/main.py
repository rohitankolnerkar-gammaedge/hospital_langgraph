from fastapi import FastAPI
from app.api.intake_api import inta
from app.db.db_config import engine
from app.db.models import Base
from app.api.enter_docter_pres import enter_docter
from app.helper.schedular import scheduler
from app.api.select_slot import select_sl
from app.api.show_available_slots import show_slots
from app.api.create_slot import router as create_slot_router
from app.api.agentic_ai import agen
from fastapi import FastAPI






app = FastAPI()
app.include_router(inta)
app.include_router(enter_docter)
app.include_router(select_sl)
app.include_router(show_slots)
app.include_router(create_slot_router)
app.include_router(agen)


@app.on_event("startup")
async def startup_event():
   Base.metadata.create_all(bind=engine)
   if not scheduler.running:
        scheduler.start()
        
   