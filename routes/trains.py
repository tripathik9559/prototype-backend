# routes/trains.py - Train Priority Data API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import Train, TrainUpdate, TrainListResponse, APIResponse
from datetime import datetime
import random

router = APIRouter()

# Mock train data storage
mock_trains = [
    {
        "id": "T001",
        "name": "Rajdhani Express",
        "type": "Express",
        "priority": 1,
        "current_location": "Platform 1",
        "status": "On Time",
        "scheduled_time": "10:30",
        "actual_time": "10:30",
        "delay": 0,
        "next_station": "New Delhi",
        "platform": 1
    },
    {
        "id": "T002",
        "name": "Shatabdi Express", 
        "type": "Express",
        "priority": 2,
        "current_location": "En Route",
        "status": "Delayed",
        "scheduled_time": "11:15",
        "actual_time": "11:25",
        "delay": 10,
        "next_station": "Mumbai Central",
        "platform": 2
    },
    {
        "id": "T003",
        "name": "Freight Express",
        "type": "Freight", 
        "priority": 3,
        "current_location": "Yard",
        "status": "Waiting",
        "scheduled_time": "12:00",
        "actual_time": "12:00",
        "delay": 0,
        "next_station": "Goods Yard",
        "platform": 4
    },
    {
        "id": "T004",
        "name": "Local Passenger",
        "type": "Passenger",
        "priority": 4, 
        "current_location": "Platform 3",
        "status": "On Time",
        "scheduled_time": "10:45",
        "actual_time": "10:45",
        "delay": 0,
        "next_station": "Suburban Station",
        "platform": 3
    }
]

@router.get("/", response_model=TrainListResponse)
async def get_all_trains(
    priority: Optional[int] = Query(None, description="Filter by priority level"),
    status: Optional[str] = Query(None, description="Filter by train status"),
    train_type: Optional[str] = Query(None, description="Filter by train type")
):
    """
    Get all trains with optional filtering by priority, status, or type
    """
    try:
        trains = mock_trains.copy()
        
        # Apply filters
        if priority:
            trains = [t for t in trains if t["priority"] == priority]
        
        if status:
            trains = [t for t in trains if t["status"].lower() == status.lower()]
            
        if train_type:
            trains = [t for t in trains if t["type"].lower() == train_type.lower()]
        
        # Sort by priority (lower number = higher priority)
        trains.sort(key=lambda x: x["priority"])
        
        return TrainListResponse(
            status="success",
            message=f"Retrieved {len(trains)} trains",
            data=trains,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trains: {str(e)}")

@router.get("/{train_id}", response_model=Train)
async def get_train_by_id(train_id: str):
    """
    Get specific train details by ID
    """
    try:
        train = next((t for t in mock_trains if t["id"] == train_id), None)
        
        if not train:
            raise HTTPException(status_code=404, detail=f"Train {train_id} not found")
        
        return Train(**train)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch train: {str(e)}")

@router.put("/{train_id}", response_model=APIResponse)
async def update_train(train_id: str, update: TrainUpdate):
    """
    Update train status, delay, or platform assignment
    """
    try:
        train_index = next((i for i, t in enumerate(mock_trains) if t["id"] == train_id), None)
        
        if train_index is None:
            raise HTTPException(status_code=404, detail=f"Train {train_id} not found")
        
        # Update train data
        if update.status:
            mock_trains[train_index]["status"] = update.status
        if update.delay is not None:
            mock_trains[train_index]["delay"] = update.delay
            # Update actual time based on delay
            scheduled_time = mock_trains[train_index]["scheduled_time"]
            # Simple time calculation (in real app, use proper datetime handling)
            hour, minute = map(int, scheduled_time.split(":"))
            new_minute = minute + update.delay
            new_hour = hour + new_minute // 60
            new_minute = new_minute % 60
            mock_trains[train_index]["actual_time"] = f"{new_hour:02d}:{new_minute:02d}"
        if update.platform:
            mock_trains[train_index]["platform"] = update.platform
        
        return APIResponse(
            status="success",
            message=f"Train {train_id} updated successfully",
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update train: {str(e)}")

@router.post("/priority/recalculate", response_model=APIResponse)
async def recalculate_priorities():
    """
    Trigger AI-based priority recalculation for all trains
    """
    try:
        # Simulate AI priority recalculation
        for train in mock_trains:
            # Mock AI logic for priority adjustment
            if train["type"] == "Express" and train["delay"] > 15:
                train["priority"] = max(1, train["priority"] - 1)  # Increase priority
            elif train["type"] == "Freight" and train["delay"] == 0:
                train["priority"] = min(5, train["priority"] + 1)  # Decrease priority
        
        # Sort by new priorities
        mock_trains.sort(key=lambda x: x["priority"])
        
        return APIResponse(
            status="success", 
            message="AI priority recalculation completed",
            data={"affected_trains": len(mock_trains)},
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priority recalculation failed: {str(e)}")

@router.get("/priority/recommendations", response_model=APIResponse)
async def get_priority_recommendations():
    """
    Get AI-generated recommendations for train priority adjustments
    """
    try:
        recommendations = []
        
        for train in mock_trains:
            # Generate mock AI recommendations
            if train["delay"] > 10 and train["type"] == "Express":
                recommendations.append({
                    "train_id": train["id"],
                    "current_priority": train["priority"],
                    "recommended_priority": max(1, train["priority"] - 1),
                    "reason": f"Express train with {train['delay']}min delay - increase priority",
                    "confidence": 0.89
                })
            elif train["type"] == "Freight" and train["delay"] == 0:
                recommendations.append({
                    "train_id": train["id"], 
                    "current_priority": train["priority"],
                    "recommended_priority": min(5, train["priority"] + 1),
                    "reason": "Freight train on-time - can reduce priority for passenger trains",
                    "confidence": 0.76
                })
        
        return APIResponse(
            status="success",
            message=f"Generated {len(recommendations)} priority recommendations",
            data=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.post("/simulate/delay/{train_id}", response_model=APIResponse)
async def simulate_train_delay(train_id: str, delay_minutes: int = Query(..., description="Delay in minutes")):
    """
    Simulate a delay for a specific train (for testing purposes)
    """
    try:
        train_index = next((i for i, t in enumerate(mock_trains) if t["id"] == train_id), None)
        
        if train_index is None:
            raise HTTPException(status_code=404, detail=f"Train {train_id} not found")
        
        # Apply delay
        mock_trains[train_index]["delay"] = delay_minutes
        mock_trains[train_index]["status"] = "Delayed" if delay_minutes > 0 else "On Time"
        
        # Update actual time
        scheduled_time = mock_trains[train_index]["scheduled_time"]
        hour, minute = map(int, scheduled_time.split(":"))
        new_minute = minute + delay_minutes
        new_hour = hour + new_minute // 60
        new_minute = new_minute % 60
        mock_trains[train_index]["actual_time"] = f"{new_hour:02d}:{new_minute:02d}"
        
        return APIResponse(
            status="success",
            message=f"Simulated {delay_minutes}-minute delay for train {train_id}",
            data=mock_trains[train_index],
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate delay: {str(e)}")