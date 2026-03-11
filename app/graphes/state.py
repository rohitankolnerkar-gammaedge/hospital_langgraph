from typing import TypedDict
from datetime import datetime
class ClinicState(TypedDict):
    patient_name: str
    Dob: str
    contact_info: str
    patient_id: str
    doctor_id: str
    appointment_time: datetime
    symptoms: str
    doctor_notes: str
    summary: str
    email:str
    appointment_status: str
    remainder_sent: bool
    status: str
    comformation_sent: bool
    Appointment_id: str
    summary_sent: bool


