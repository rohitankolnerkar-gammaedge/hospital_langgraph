from app.graphes.state import ClinicState
from app.db.db_config import SessionLocal
from app.db.models import PatientRecord 
   
def create_patient_record(state: ClinicState):
    db = SessionLocal()
    print("STATE RECEIVED:", state)
    email = state.get("email")
    patient = db.query(PatientRecord).filter(PatientRecord.email == email).first()

    if patient:
       
        patient.patient_name = state.get("patient_name", patient.patient_name)
        patient.dob = state.get("dob", patient.dob)
        patient.symptoms = state.get("symptoms", patient.symptoms)
        print(f"Patient record created/updated for {patient.patient_name} with email {patient.email}")
        db.commit()
        db.refresh(patient)

    else:
        patient = PatientRecord(
            patient_name=state.get("patient_name"),
            dob=state.get("dob"),
            email=email,
            phone=state.get("phone"),
            symptoms=state.get("symptoms"),
        )
        print(f"Patient record created/updated for {patient.patient_name} with email {patient.email}")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    
    db.close()
    
    

    return {"patient_id": patient.id, "status": "record_created"}
    