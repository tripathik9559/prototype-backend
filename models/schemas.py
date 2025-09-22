# models/schemas.py - Pydantic Schemas for API Responses
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TrainType(str, Enum):
    EXPRESS = "Express"
    PASSENGER = "Passenger" 
    FREIGHT = "Freight"

class TrainStatus(str, Enum):
    ON_TIME = "On Time"
    DELAYED = "Delayed"
    WAITING = "Waiting"
    CANCELLED = "Cancelled"
    EN_ROUTE = "En Route"

class PlatformStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    MAINTENANCE = "Maintenance"

class ConflictSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

# Train-related schemas
class TrainBase(BaseModel):
    id: str = Field(..., description="Unique train identifier")
    name: str = Field(..., description="Train name")
    type: TrainType = Field(..., description="Type of train")
    priority: int = Field(..., ge=1, le=5, description="Train priority (1=highest)")

class Train(TrainBase):
    current_location: str = Field(..., description="Current location")
    status: TrainStatus = Field(..., description="Current status")
    scheduled_time: str = Field(..., description="Scheduled departure/arrival time")
    actual_time: str = Field(..., description="Actual departure/arrival time")
    delay: int = Field(default=0, description="Delay in minutes")
    next_station: str = Field(..., description="Next destination")
    platform: Optional[int] = Field(None, description="Assigned platform number")

class TrainUpdate(BaseModel):
    id: str
    status: Optional[TrainStatus] = None
    delay: Optional[int] = None
    platform: Optional[int] = None

# Platform-related schemas
class Platform(BaseModel):
    id: int = Field(..., description="Platform number")
    status: PlatformStatus = Field(..., description="Platform status")
    train: Optional[str] = Field(None, description="Train ID currently using platform")
    next_available: str = Field(..., description="Next available time")

# Conflict-related schemas
class Conflict(BaseModel):
    id: str = Field(..., description="Conflict identifier")
    type: str = Field(..., description="Type of conflict")
    trains: List[str] = Field(..., description="Involved train IDs")
    platform: Optional[int] = Field(None, description="Platform involved in conflict")
    severity: ConflictSeverity = Field(..., description="Severity level")
    time: str = Field(..., description="Time when conflict detected")
    resolution: Optional[str] = Field(None, description="Proposed resolution")

# Schedule-related schemas
class ScheduleEntry(BaseModel):
    train_id: str
    departure_time: str
    arrival_time: str
    platform: int
    route: List[str]
    estimated_delay: int = 0

class Schedule(BaseModel):
    entries: List[ScheduleEntry]
    last_updated: str
    conflicts_count: int = 0

# Analytics schemas
class ThroughputData(BaseModel):
    labels: List[str] = Field(..., description="Time labels")
    values: List[int] = Field(..., description="Throughput values")

class DelayDistribution(BaseModel):
    on_time: float = Field(..., description="Percentage on time")
    delayed: float = Field(..., description="Percentage delayed") 
    cancelled: float = Field(..., description="Percentage cancelled")

class PlatformUtilization(BaseModel):
    platform1: float
    platform2: float
    platform3: float
    platform4: float
    platform5: float
    platform6: float

class AnalyticsData(BaseModel):
    throughput: ThroughputData
    delays: DelayDistribution
    platform_utilization: PlatformUtilization

# Optimization schemas
class OptimizationRequest(BaseModel):
    trains: List[Train]
    platforms: List[Platform]
    constraints: Optional[Dict[str, Any]] = None

class OptimizationResult(BaseModel):
    success: bool
    optimized_schedule: List[ScheduleEntry]
    improvements: Dict[str, float]
    execution_time: float
    algorithm_used: str

# Scenario simulation schemas
class ScenarioType(str, Enum):
    NORMAL = "normal"
    PEAK_HOURS = "peak_hours"
    WEATHER = "weather"
    ACCIDENT = "accident"
    MAINTENANCE = "maintenance"
    SIGNAL_FAILURE = "signal_failure"

class ScenarioSimulation(BaseModel):
    scenario: ScenarioType
    affected_trains: List[str]
    impact_description: str
    estimated_delay: int
    recovery_time: int

# Response schemas
class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None
    timestamp: str

class TrainListResponse(APIResponse):
    data: List[Train]

class PlatformListResponse(APIResponse):
    data: List[Platform]

class ConflictListResponse(APIResponse):
    data: List[Conflict]

class AnalyticsResponse(APIResponse):
    data: AnalyticsData

# Real-time update schemas
class RealTimeUpdate(BaseModel):
    timestamp: str
    update_type: str  # "train_status", "platform_change", "conflict_detected", etc.
    data: Dict[str, Any]

class SystemStatus(BaseModel):
    active_trains: int
    available_platforms: int
    current_conflicts: int
    system_health: str
    last_optimization: str