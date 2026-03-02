from dataclasses import dataclass
from datetime import date, timedelta, datetime
from enum import Enum
from typing import Optional


# --- ENUMY ---

class School(Enum):
    PODSTAWOWE = "PODSTAWOWE"
    SREDNIE = "SREDNIE"
    WYZSZE = "WYZSZE"


class SchoolDetails(Enum):
    KLASA1 = "KLASA1"
    KLASA2 = "KLASA2"
    KLASA3 = "KLASA3"
    KLASA4 = "KLASA4"
    KLASA5 = "KLASA5"
    KLASA6 = "KLASA6"
    KLASA7 = "KLASA7"
    KLASA8 = "KLASA8"
    TECHNIKUM = "TECHNIKUM"
    LICEUM = "LICEUM"
    LICENCJAT = "LICENCJAT"
    MAGISTER = "MAGISTER"
    DOKTORAT = "DOKTORAT"
    EDUKACJA_ZAKONCZONE = "EDUKACJA_ZAKONCZONE"


class Hand(Enum):
    PRAWA = "PRAWA"
    LEWA = "LEWA"


class Gender(Enum):
    MEZCZYZNA = "MEZCZYZNA"
    KOBIETA = "KOBIETA"


# --- MODELE DANYCH ---

@dataclass
class Patient:
    id: Optional[int]
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    dominant_hand: Hand


@dataclass
class Examination:
    id: Optional[int]
    patient_id: int
    date: date
    whole_time: Optional[timedelta]
    avg_time: Optional[timedelta]
    age_years: int
    age_months: int
    age_days: int
    visual_impairment: bool
    impairment_description: Optional[str]
    education: School
    education_details: SchoolDetails
    comments: Optional[str]
    examination_reason: Optional[str]
    total_duration_s: float
    test_start_ts: float
    test_end_ts: datetime


@dataclass
class Image:
    id: Optional[int]
    examine_id: int
    content: bytes
    started_at_ts: datetime
    first_stroke_at_ts: datetime
    finished_at_ts: datetime
    interruptions_count: int
    interruptions_durations: list[float]
    undo_count: int
    redo_count: int
    overdrawing_score: float
    revisit_count: int
    shading_detected: bool
    direction_changes_count: int
    direction_reversal_count: int
    rapid_velocity_changes_count: int
    efficiency_ratio: float
    max_local_density: float
    max_local_density_coords: list[int]
    avg_velocity: float
    max_velocity: float
    velocity_ratio: float
    velocities: list[float]
    velocity_profile_filename: str
    overlay_filename: str
    heatmap_filename: str
    duration_s: float
    actual_drawing_duration_s: float
    avg_interruption_duration_s: float


@dataclass
class Failure:
    id: Optional[int]
    image_id: int
    pominiecia: int
    znieksztalcenia: int
    perserwacje: int
    rotacje: int
    przemieszczenia: int
    bledy_wzglednej_wielkosci: int


@dataclass
class TestMetaData:
    examine_id: int
    patient_id: int


@dataclass
class PatientSummaryDTO:
    id: Optional[int]
    age_years: int
    age_months: int
    age_days: int
    gender: Gender
    dominant_hand: Hand
    visual_impairment: bool
    impairment_description: Optional[str]
    comment: Optional[str]


@dataclass
class ImageTableDataSummary:
    idx: int
    examine_id: int
    content: bytes
    duration_s: float
    is_valid: bool
    failures: list[int]


@dataclass
class PreviousExaminationsDTO:
    patient_id: int
    examine_id: int
    failure_mappings: int
    valid_mappings: int
    avg_time: timedelta
    whole_time: timedelta
    pominiecia: int
    znieksztalcenia: int
    perserwacje: int
    rotacje: int
    przemieszczenia: int
    bledy_wzglednej_wielkosci: int
    result: str
    comment: Optional[str]
    examine_date: date


@dataclass
class PatientIdentity:
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    dominant_hand: Hand
