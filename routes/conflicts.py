# routes/conflicts.py - Conflict Detection API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from models.schemas import Conflict, ConflictListResponse, APIResponse, ConflictSeverity
from datetime import datetime
import random

router = APIRouter()

# Mock conflict data storage
mock_conflicts = [
    {
        "id": "conflict_001",
        "type": "Platform Conflict",
        "trains": ["T001", "T002"],
        "platform": 2,
        "severity": "High",
        "time": "10:45:00",
        "resolution": "Reschedule T002 to Platform 5 with 5-minute delay"
    },
    {
        "id": "conflict_002", 
        "type": "Signal Timing",
        "trains": ["T003", "T004"],
        "platform": None,
        "severity": "Medium",
        "time": "11:30:15",
        "resolution": "Adjust signal timing for T004 by 3 minutes"
    }
]

@router.get("/", response_model=ConflictListResponse)
async def get_all_conflicts(
    severity: Optional[ConflictSeverity] = Query(None, description="Filter by severity level"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status")
):
    """
    Get all detected conflicts with optional filtering
    """
    try:
        conflicts = mock_conflicts.copy()
        
        # Apply filters
        if severity:
            conflicts = [c for c in conflicts if c["severity"] == severity.value]
        
        if resolved is not None:
            # For demo, assume conflicts with resolutions are resolved
            if resolved:
                conflicts = [c for c in conflicts if c.get("resolution")]
            else:
                conflicts = [c for c in conflicts if not c.get("resolution")]
        
        return ConflictListResponse(
            status="success",
            message=f"Retrieved {len(conflicts)} conflicts",
            data=[Conflict(**conflict) for conflict in conflicts],
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch conflicts: {str(e)}")

@router.get("/{conflict_id}", response_model=APIResponse)
async def get_conflict_by_id(conflict_id: str):
    """
    Get specific conflict details by ID
    """
    try:
        conflict = next((c for c in mock_conflicts if c["id"] == conflict_id), None)
        
        if not conflict:
            raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
        
        return APIResponse(
            status="success",
            message=f"Conflict {conflict_id} retrieved",
            data=Conflict(**conflict),
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch conflict: {str(e)}")

@router.post("/detect", response_model=APIResponse)
async def detect_conflicts():
    """
    Run real-time conflict detection algorithm on current train schedules
    """
    try:
        # Simulate conflict detection algorithm
        detected_conflicts = []
        
        # Mock detection logic - check for platform conflicts
        train_schedules = [
            {"id": "T001", "platform": 1, "time": "10:30", "duration": 10},
            {"id": "T002", "platform": 2, "time": "11:15", "duration": 8},
            {"id": "T003", "platform": 4, "time": "12:00", "duration": 15},
            {"id": "T004", "platform": 3, "time": "10:45", "duration": 12}
        ]
        
        # Check for overlapping platform usage
        for i, train1 in enumerate(train_schedules):
            for j, train2 in enumerate(train_schedules[i+1:], i+1):
                if train1["platform"] == train2["platform"]:
                    # Calculate time overlap
                    time1 = int(train1["time"].replace(":", ""))
                    time2 = int(train2["time"].replace(":", ""))
                    
                    if abs(time1 - time2) < 30:  # Less than 30-minute gap
                        conflict_id = f"conflict_{random.randint(100, 999)}"
                        severity = "High" if abs(time1 - time2) < 15 else "Medium"
                        
                        new_conflict = {
                            "id": conflict_id,
                            "type": "Platform Scheduling Conflict",
                            "trains": [train1["id"], train2["id"]],
                            "platform": train1["platform"],
                            "severity": severity,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "resolution": None
                        }
                        
                        detected_conflicts.append(new_conflict)
                        mock_conflicts.append(new_conflict)
        
        # Simulate signal conflicts
        if random.random() < 0.3:  # 30% chance of signal conflict
            signal_conflict = {
                "id": f"signal_conflict_{random.randint(100, 999)}",
                "type": "Signal Timing Conflict",
                "trains": [random.choice(["T001", "T002", "T003", "T004"]), 
                          random.choice(["T001", "T002", "T003", "T004"])],
                "platform": None,
                "severity": random.choice(["Low", "Medium"]),
                "time": datetime.now().strftime("%H:%M:%S"),
                "resolution": None
            }
            detected_conflicts.append(signal_conflict)
            mock_conflicts.append(signal_conflict)
        
        return APIResponse(
            status="success",
            message=f"Conflict detection completed. {len(detected_conflicts)} new conflicts found.",
            data={
                "new_conflicts": detected_conflicts,
                "total_active_conflicts": len([c for c in mock_conflicts if not c.get("resolution")]),
                "detection_algorithm": "AI-Powered Real-Time Conflict Detection",
                "scan_duration": f"{random.uniform(0.1, 0.5):.2f} seconds"
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conflict detection failed: {str(e)}")

@router.post("/{conflict_id}/resolve", response_model=APIResponse)
async def resolve_conflict(conflict_id: str, resolution_method: str = Query(..., description="Resolution method to apply")):
    """
    Apply AI-generated resolution to a specific conflict
    """
    try:
        conflict_index = next((i for i, c in enumerate(mock_conflicts) if c["id"] == conflict_id), None)
        
        if conflict_index is None:
            raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")
        
        conflict = mock_conflicts[conflict_index]
        
        # Generate resolution based on conflict type and method
        resolutions = {
            "reschedule": f"Reschedule {conflict['trains'][1]} by 10 minutes to avoid platform overlap",
            "platform_change": f"Move {conflict['trains'][0]} to alternate platform {random.randint(5, 8)}",
            "signal_adjust": f"Adjust signal timing for {conflict['trains'][1]} by 5-minute buffer",
            "route_change": f"Reroute {conflict['trains'][1]} through alternate track section",
            "priority_override": f"Apply priority override for {conflict['trains'][0]} (higher priority train)"
        }
        
        resolution_text = resolutions.get(resolution_method, f"Apply {resolution_method} resolution")
        
        # Update conflict with resolution
        mock_conflicts[conflict_index]["resolution"] = resolution_text
        mock_conflicts[conflict_index]["resolved_time"] = datetime.now().isoformat()
        mock_conflicts[conflict_index]["resolution_method"] = resolution_method
        
        # Simulate resolution success rate
        success_rate = random.uniform(0.85, 0.98)
        
        return APIResponse(
            status="success",
            message=f"Conflict {conflict_id} resolved using {resolution_method}",
            data={
                "conflict_id": conflict_id,
                "resolution": resolution_text,
                "success_probability": round(success_rate, 2),
                "affected_trains": conflict["trains"],
                "resolution_time": datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve conflict: {str(e)}")

@router.get("/predictions/upcoming", response_model=APIResponse)
async def predict_upcoming_conflicts():
    """
    Use AI to predict potential conflicts in the next few hours
    """
    try:
        # Simulate AI prediction algorithm
        predictions = []
        
        # Generate mock predictions
        for i in range(random.randint(1, 4)):
            prediction = {
                "predicted_time": f"{random.randint(12, 18):02d}:{random.randint(0, 59):02d}",
                "conflict_type": random.choice(["Platform Overlap", "Signal Timing", "Route Crossing"]),
                "involved_trains": [
                    f"T{random.randint(5, 9):03d}",
                    f"T{random.randint(5, 9):03d}"
                ],
                "probability": random.uniform(0.6, 0.9),
                "severity": random.choice(["Medium", "High"]),
                "preventive_action": random.choice([
                    "Adjust departure time by 5 minutes",
                    "Reserve alternate platform", 
                    "Increase buffer time between trains",
                    "Implement speed restriction"
                ])
            }
            predictions.append(prediction)
        
        return APIResponse(
            status="success",
            message=f"Generated {len(predictions)} conflict predictions",
            data={
                "predictions": predictions,
                "prediction_horizon": "6 hours",
                "model_accuracy": "92.5%",
                "last_model_update": "2025-01-20T08:00:00Z"
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")

@router.post("/prevention/auto", response_model=APIResponse)
async def enable_auto_prevention():
    """
    Enable automatic conflict prevention system
    """
    try:
        # Simulate enabling auto-prevention
        prevention_rules = [
            "Maintain minimum 5-minute buffer between platform assignments",
            "Auto-reschedule conflicting trains with <70% probability threshold",
            "Prioritize Express trains during conflict resolution",
            "Enable dynamic platform reallocation for freight trains",
            "Implement early warning system 30 minutes before predicted conflicts"
        ]
        
        return APIResponse(
            status="success",
            message="Automatic conflict prevention enabled",
            data={
                "prevention_rules": prevention_rules,
                "enabled_features": [
                    "Real-time conflict detection",
                    "Predictive conflict analysis", 
                    "Automatic resolution suggestions",
                    "Dynamic schedule adjustment"
                ],
                "monitoring_interval": "30 seconds",
                "ai_confidence_threshold": 0.75
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable auto-prevention: {str(e)}")

@router.get("/statistics", response_model=APIResponse)
async def get_conflict_statistics():
    """
    Get comprehensive statistics about conflicts and resolution performance
    """
    try:
        total_conflicts = len(mock_conflicts)
        resolved_conflicts = len([c for c in mock_conflicts if c.get("resolution")])
        active_conflicts = total_conflicts - resolved_conflicts
        
        # Generate statistics
        stats = {
            "total_conflicts_detected": total_conflicts,
            "resolved_conflicts": resolved_conflicts,
            "active_conflicts": active_conflicts,
            "resolution_rate": round((resolved_conflicts / total_conflicts) * 100, 1) if total_conflicts > 0 else 0,
            "severity_breakdown": {
                "critical": len([c for c in mock_conflicts if c["severity"] == "Critical"]),
                "high": len([c for c in mock_conflicts if c["severity"] == "High"]),
                "medium": len([c for c in mock_conflicts if c["severity"] == "Medium"]),
                "low": len([c for c in mock_conflicts if c["severity"] == "Low"])
            },
            "conflict_types": {
                "platform": len([c for c in mock_conflicts if "Platform" in c["type"]]),
                "signal": len([c for c in mock_conflicts if "Signal" in c["type"]]),
                "route": len([c for c in mock_conflicts if "Route" in c["type"]])
            },
            "average_resolution_time": f"{random.uniform(2.5, 8.5):.1f} minutes",
            "prevention_success_rate": f"{random.uniform(88, 96):.1f}%"
        }
        
        return APIResponse(
            status="success",
            message="Conflict statistics generated",
            data=stats,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate statistics: {str(e)}")