# routes/schedule.py - Schedule & Delay Management API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from models.schemas import Schedule, ScheduleEntry, APIResponse, ScenarioType
from datetime import datetime, timedelta
import random

router = APIRouter()

# Mock schedule data
mock_schedule_entries = [
    {
        "train_id": "T001",
        "departure_time": "10:30",
        "arrival_time": "10:25",
        "platform": 1,
        "route": ["Platform 1", "Signal A", "Main Line", "New Delhi"],
        "estimated_delay": 0
    },
    {
        "train_id": "T002", 
        "departure_time": "11:15",
        "arrival_time": "11:10",
        "platform": 2,
        "route": ["Platform 2", "Signal B", "Express Line", "Mumbai Central"],
        "estimated_delay": 10
    },
    {
        "train_id": "T003",
        "departure_time": "12:00", 
        "arrival_time": "11:55",
        "platform": 4,
        "route": ["Platform 4", "Goods Yard", "Freight Line", "Industrial Zone"],
        "estimated_delay": 0
    },
    {
        "train_id": "T004",
        "departure_time": "10:45",
        "arrival_time": "10:40", 
        "platform": 3,
        "route": ["Platform 3", "Local Line", "Suburban Stations"],
        "estimated_delay": 0
    }
]

@router.get("/current", response_model=APIResponse)
async def get_current_schedule():
    """
    Get the current train schedule with all entries
    """
    try:
        schedule = Schedule(
            entries=[ScheduleEntry(**entry) for entry in mock_schedule_entries],
            last_updated=datetime.now().isoformat(),
            conflicts_count=len([e for e in mock_schedule_entries if e["estimated_delay"] > 0])
        )
        
        return APIResponse(
            status="success",
            message="Current schedule retrieved successfully",
            data=schedule.dict(),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schedule: {str(e)}")

@router.get("/train/{train_id}", response_model=APIResponse) 
async def get_train_schedule(train_id: str):
    """
    Get schedule details for a specific train
    """
    try:
        entry = next((e for e in mock_schedule_entries if e["train_id"] == train_id), None)
        
        if not entry:
            raise HTTPException(status_code=404, detail=f"Schedule not found for train {train_id}")
        
        return APIResponse(
            status="success",
            message=f"Schedule retrieved for train {train_id}",
            data=entry,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch train schedule: {str(e)}")

@router.put("/train/{train_id}/delay", response_model=APIResponse)
async def update_train_delay(
    train_id: str, 
    delay_minutes: int = Query(..., description="Delay in minutes"),
    reason: Optional[str] = Query(None, description="Reason for delay")
):
    """
    Update delay for a specific train and recalculate affected schedules
    """
    try:
        entry_index = next((i for i, e in enumerate(mock_schedule_entries) if e["train_id"] == train_id), None)
        
        if entry_index is None:
            raise HTTPException(status_code=404, detail=f"Train {train_id} not found in schedule")
        
        # Update the delay
        mock_schedule_entries[entry_index]["estimated_delay"] = delay_minutes
        
        # Update departure time based on delay
        original_time = mock_schedule_entries[entry_index]["departure_time"]
        hour, minute = map(int, original_time.split(":"))
        new_minute = minute + delay_minutes
        new_hour = hour + new_minute // 60
        new_minute = new_minute % 60
        updated_time = f"{new_hour:02d}:{new_minute:02d}"
        
        # Simulate cascade effect on other trains (simplified)
        affected_trains = []
        for i, entry in enumerate(mock_schedule_entries):
            if i != entry_index and entry["platform"] == mock_schedule_entries[entry_index]["platform"]:
                # Add minor delay to trains using the same platform
                if delay_minutes > 15:
                    mock_schedule_entries[i]["estimated_delay"] += min(5, delay_minutes // 3)
                    affected_trains.append(entry["train_id"])
        
        return APIResponse(
            status="success",
            message=f"Delay updated for train {train_id}. {len(affected_trains)} other trains affected.",
            data={
                "updated_train": train_id,
                "new_delay": delay_minutes,
                "updated_departure": updated_time,
                "affected_trains": affected_trains,
                "reason": reason or "Manual delay update"
            },
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update delay: {str(e)}")

@router.post("/optimize", response_model=APIResponse)
async def optimize_schedule():
    """
    Run AI optimization on the current schedule to minimize delays and conflicts
    """
    try:
        # Simulate AI optimization process
        optimizations_made = []
        total_delay_before = sum(e["estimated_delay"] for e in mock_schedule_entries)
        
        # Mock optimization logic
        for i, entry in enumerate(mock_schedule_entries):
            if entry["estimated_delay"] > 10:
                # Try to reduce delay through rescheduling
                original_delay = entry["estimated_delay"]
                optimized_delay = max(0, original_delay - random.randint(3, 8))
                mock_schedule_entries[i]["estimated_delay"] = optimized_delay
                
                if optimized_delay < original_delay:
                    optimizations_made.append({
                        "train_id": entry["train_id"],
                        "original_delay": original_delay,
                        "optimized_delay": optimized_delay,
                        "improvement": original_delay - optimized_delay
                    })
        
        total_delay_after = sum(e["estimated_delay"] for e in mock_schedule_entries)
        
        return APIResponse(
            status="success",
            message="Schedule optimization completed",
            data={
                "optimizations_made": len(optimizations_made),
                "total_delay_reduction": total_delay_before - total_delay_after,
                "details": optimizations_made,
                "algorithm": "AI-Powered Dynamic Scheduling",
                "execution_time": f"{random.uniform(0.5, 2.0):.2f} seconds"
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule optimization failed: {str(e)}")

@router.post("/scenario/{scenario_type}", response_model=APIResponse)
async def apply_scenario(scenario_type: ScenarioType):
    """
    Apply a specific scenario (weather, accident, etc.) and update schedule accordingly
    """
    try:
        affected_trains = []
        scenario_effects = {}
        
        if scenario_type == ScenarioType.WEATHER:
            # Weather scenario: add delays to non-freight trains
            for i, entry in enumerate(mock_schedule_entries):
                if "Express" in entry["train_id"] or "Passenger" in entry["train_id"]:
                    additional_delay = random.randint(10, 30)
                    mock_schedule_entries[i]["estimated_delay"] += additional_delay
                    affected_trains.append(entry["train_id"])
            
            scenario_effects = {
                "type": "Weather Disruption",
                "description": "Heavy rain causing speed restrictions",
                "affected_count": len(affected_trains),
                "average_additional_delay": 20
            }
        
        elif scenario_type == ScenarioType.ACCIDENT:
            # Accident scenario: major delays for all trains
            for i, entry in enumerate(mock_schedule_entries):
                additional_delay = random.randint(30, 60)
                mock_schedule_entries[i]["estimated_delay"] += additional_delay
                affected_trains.append(entry["train_id"])
            
            scenario_effects = {
                "type": "Track Accident",
                "description": "Emergency situation requiring rerouting",
                "affected_count": len(affected_trains),
                "average_additional_delay": 45
            }
        
        elif scenario_type == ScenarioType.PEAK_HOURS:
            # Peak hours: moderate delays due to congestion
            for i, entry in enumerate(mock_schedule_entries):
                if "Express" in entry["train_id"] or "Passenger" in entry["train_id"]:
                    additional_delay = random.randint(5, 15)
                    mock_schedule_entries[i]["estimated_delay"] += additional_delay
                    affected_trains.append(entry["train_id"])
            
            scenario_effects = {
                "type": "Peak Hour Congestion",
                "description": "High passenger volume causing delays", 
                "affected_count": len(affected_trains),
                "average_additional_delay": 10
            }
        
        elif scenario_type == ScenarioType.MAINTENANCE:
            # Maintenance scenario: platform availability reduced
            maintenance_platform = random.randint(1, 4)
            for i, entry in enumerate(mock_schedule_entries):
                if entry["platform"] == maintenance_platform:
                    # Reassign to different platform with delay
                    new_platform = (maintenance_platform % 4) + 1
                    mock_schedule_entries[i]["platform"] = new_platform
                    mock_schedule_entries[i]["estimated_delay"] += random.randint(15, 25)
                    affected_trains.append(entry["train_id"])
            
            scenario_effects = {
                "type": "Scheduled Maintenance",
                "description": f"Platform {maintenance_platform} under maintenance",
                "affected_count": len(affected_trains),
                "maintenance_platform": maintenance_platform
            }
        
        else:
            # Normal operations - reset delays
            for i, entry in enumerate(mock_schedule_entries):
                mock_schedule_entries[i]["estimated_delay"] = 0
            
            scenario_effects = {
                "type": "Normal Operations",
                "description": "All systems operating normally",
                "affected_count": 0
            }
        
        return APIResponse(
            status="success",
            message=f"Scenario '{scenario_type}' applied successfully",
            data={
                "scenario": scenario_effects,
                "affected_trains": affected_trains,
                "updated_schedule": mock_schedule_entries
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply scenario: {str(e)}")

@router.get("/delays/summary", response_model=APIResponse)
async def get_delay_summary():
    """
    Get summary of current delays across all trains
    """
    try:
        total_trains = len(mock_schedule_entries)
        delayed_trains = [e for e in mock_schedule_entries if e["estimated_delay"] > 0]
        on_time_trains = total_trains - len(delayed_trains)
        
        total_delay_minutes = sum(e["estimated_delay"] for e in mock_schedule_entries)
        average_delay = total_delay_minutes / total_trains if total_trains > 0 else 0
        
        delay_categories = {
            "minor": len([e for e in delayed_trains if 0 < e["estimated_delay"] <= 10]),
            "moderate": len([e for e in delayed_trains if 10 < e["estimated_delay"] <= 30]),
            "major": len([e for e in delayed_trains if e["estimated_delay"] > 30])
        }
        
        return APIResponse(
            status="success",
            message="Delay summary generated",
            data={
                "total_trains": total_trains,
                "on_time_trains": on_time_trains,
                "delayed_trains": len(delayed_trains),
                "total_delay_minutes": total_delay_minutes,
                "average_delay": round(average_delay, 2),
                "delay_categories": delay_categories,
                "on_time_percentage": round((on_time_trains / total_trains) * 100, 1)
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate delay summary: {str(e)}")

@router.post("/reschedule/batch", response_model=APIResponse)
async def batch_reschedule(train_ids: List[str], new_departure_times: List[str]):
    """
    Reschedule multiple trains at once
    """
    try:
        if len(train_ids) != len(new_departure_times):
            raise HTTPException(status_code=400, detail="Number of train IDs must match number of departure times")
        
        updated_trains = []
        
        for train_id, new_time in zip(train_ids, new_departure_times):
            entry_index = next((i for i, e in enumerate(mock_schedule_entries) if e["train_id"] == train_id), None)
            
            if entry_index is not None:
                old_time = mock_schedule_entries[entry_index]["departure_time"]
                mock_schedule_entries[entry_index]["departure_time"] = new_time
                
                # Recalculate delay based on new time
                # (Simplified calculation)
                mock_schedule_entries[entry_index]["estimated_delay"] = 0  # Reset delay after reschedule
                
                updated_trains.append({
                    "train_id": train_id,
                    "old_departure_time": old_time,
                    "new_departure_time": new_time
                })
        
        return APIResponse(
            status="success",
            message=f"Batch rescheduling completed for {len(updated_trains)} trains",
            data={
                "updated_trains": updated_trains,
                "rescheduled_count": len(updated_trains)
            },
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch rescheduling failed: {str(e)}")