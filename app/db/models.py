from sqlalchemy import Column, Integer, String,ForeignKey,Boolean,DateTime
from sqlalchemy.orm import declarative_base,relationship

Base = declarative_base()

class PatientRecord(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    dob = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    doctor_id = Column(Integer, nullable=True)
    symptoms = Column(String)
    doctor_notes = Column(String, default="")

    appointments = relationship("Appointment", back_populates="patient")
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"))

    appointment_time = Column(DateTime,nullable=True)
    status = Column(String, default="scheduled")

    reminder_sent = Column(Boolean, default=False)

    summary = Column(String, default="")
    summary_sent = Column(Boolean, default=False)

    patient = relationship("PatientRecord", back_populates="appointments")

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedule"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer)
    slot_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)







    
        