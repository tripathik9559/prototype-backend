# routes/kpis.py - Analytics & KPIs API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from models.schemas import AnalyticsData, AnalyticsResponse, APIResponse
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics():
    """
    Get comprehensive analytics data for the main dashboard
    """
    try:
        # Generate mock analytics data
        analytics_data = AnalyticsData(
            throughput={
                "labels": ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
                "values": [12, 18, 25, 22, 28, 24, 20, 15]
            },
            delays={
                "on_time": 75.3,
                "delayed": 19.2,
                "cancelled": 5.5
            },
            platform_utilization={
                "platform1": 85.2,
                "platform2": 67.8,
                "platform3": 78.4,
                "platform4": 45.1,
                "platform5": 30.7,
                "platform6": 12.3
            }
        )
        
        return AnalyticsResponse(
            status="success",
            message="Dashboard analytics retrieved successfully",
            data=analytics_data,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@router.get("/throughput", response_model=APIResponse)
async def get_throughput_analysis(
    period: str = Query("24h", description="Time period: 1h, 6h, 24h, 7d"),
    train_type: Optional[str] = Query(None, description="Filter by train type")
):
    """
    Get detailed throughput analysis for specified time period
    """
    try:
        # Generate different data based on period
        if period == "1h":
            labels = [f"{i:02d}:00" for i in range(max(0, datetime.now().hour - 1), datetime.now().hour + 1)]
            values = [random.randint(2, 6) for _ in labels]
        elif period == "6h":
            labels = [f"{(datetime.now().hour - 6 + i) % 24:02d}:00" for i in range(7)]
            values = [random.randint(8, 15) for _ in labels]
        elif period == "24h":
            labels = [f"{i:02d}:00" for i in range(0, 24, 3)]
            values = [random.randint(5, 30) for _ in labels]
        else:  # 7d
            labels = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
            values = [random.randint(150, 250) for _ in labels]
        
        # Apply train type filter
        filter_multiplier = 1.0
        if train_type:
            if train_type.lower() == "express":
                filter_multiplier = 0.4  # Express trains are 40% of total
            elif train_type.lower() == "passenger":
                filter_multiplier = 0.5  # Passenger trains are 50% of total  
            elif train_type.lower() == "freight":
                filter_multiplier = 0.1  # Freight trains are 10% of total
        
        filtered_values = [int(v * filter_multiplier) for v in values]
        
        # Calculate metrics
        total_trains = sum(filtered_values)
        average_per_period = total_trains / len(filtered_values) if filtered_values else 0
        peak_throughput = max(filtered_values) if filtered_values else 0
        peak_time = labels[filtered_values.index(peak_throughput)] if filtered_values else "N/A"
        
        return APIResponse(
            status="success",
            message=f"Throughput analysis for {period} period",
            data={
                "period": period,
                "train_type_filter": train_type,
                "throughput_data": {
                    "labels": labels,
                    "values": filtered_values
                },
                "metrics": {
                    "total_trains": total_trains,
                    "average_per_period": round(average_per_period, 1),
                    "peak_throughput": peak_throughput,
                    "peak_time": peak_time,
                    "efficiency_score": round(random.uniform(85, 95), 1)
                }
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze throughput: {str(e)}")

@router.get("/delays", response_model=APIResponse)
async def get_delay_analytics():
    """
    Get comprehensive delay analytics and patterns
    """
    try:
        # Generate delay analytics
        delay_data = {
            "current_status": {
                "on_time": 75.3,
                "minor_delay": 15.2,  # 1-10 minutes
                "moderate_delay": 6.8,  # 11-30 minutes
                "major_delay": 2.7   # >30 minutes
            },
            "delay_trends": {
                "hourly_pattern": {
                    "labels": [f"{i:02d}:00" for i in range(6, 23)],
                    "avg_delays": [random.uniform(2, 15) for _ in range(17)]
                },
                "daily_pattern": {
                    "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    "avg_delays": [8.2, 7.8, 9.1, 8.9, 12.3, 6.5, 5.2]
                }
            },
            "delay_causes": {
                "weather": 25.4,
                "signal_issues": 18.7,
                "passenger_boarding": 15.3,
                "track_maintenance": 12.8,
                "congestion": 10.9,
                "technical_issues": 8.2,
                "other": 8.7
            },
            "improvement_metrics": {
                "avg_delay_reduction": 2.3,  # minutes reduced compared to last month
                "on_time_improvement": 4.7,  # percentage improvement
                "ai_optimization_impact": 15.8  # percentage of delays prevented by AI
            }
        }
        
        return APIResponse(
            status="success",
            message="Delay analytics retrieved successfully",
            data=delay_data,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch delay analytics: {str(e)}")

@router.get("/platforms", response_model=APIResponse)
async def get_platform_analytics():
    """
    Get detailed platform utilization and efficiency metrics
    """
    try:
        platforms_data = {
            "utilization_summary": {
                "average_utilization": 58.7,
                "peak_utilization": 95.2,
                "off_peak_utilization": 22.1,
                "optimal_utilization_range": "65-85%"
            },
            "platform_details": [
                {
                    "platform_id": 1,
                    "utilization_rate": 85.2,
                    "trains_per_day": 48,
                    "average_turnaround": 8.5,  # minutes
                    "efficiency_score": 92.1,
                    "primary_train_types": ["Express", "Passenger"]
                },
                {
                    "platform_id": 2,
                    "utilization_rate": 67.8,
                    "trains_per_day": 36,
                    "average_turnaround": 10.2,
                    "efficiency_score": 78.4,
                    "primary_train_types": ["Express", "Freight"]
                },
                {
                    "platform_id": 3,
                    "utilization_rate": 78.4,
                    "trains_per_day": 42,
                    "average_turnaround": 9.1,
                    "efficiency_score": 85.6,
                    "primary_train_types": ["Passenger"]
                },
                {
                    "platform_id": 4,
                    "utilization_rate": 45.1,
                    "trains_per_day": 24,
                    "average_turnaround": 15.3,
                    "efficiency_score": 72.8,
                    "primary_train_types": ["Freight"]
                },
                {
                    "platform_id": 5,
                    "utilization_rate": 30.7,
                    "trains_per_day": 18,
                    "average_turnaround": 7.8,
                    "efficiency_score": 68.2,
                    "primary_train_types": ["Passenger"]
                },
                {
                    "platform_id": 6,
                    "utilization_rate": 12.3,
                    "trains_per_day": 8,
                    "average_turnaround": 20.1,
                    "efficiency_score": 45.5,
                    "primary_train_types": ["Maintenance", "Emergency"]
                }
            ],
            "optimization_suggestions": [
                "Platform 6 underutilized - consider scheduling more passenger trains",
                "Platform 1 at optimal capacity - maintain current allocation",
                "Platform 4 turnaround time above average - investigate freight handling delays"
            ]
        }
        
        return APIResponse(
            status="success",
            message="Platform analytics retrieved successfully",
            data=platforms_data,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch platform analytics: {str(e)}")

@router.get("/performance", response_model=APIResponse)
async def get_performance_metrics():
    """
    Get overall system performance metrics and KPIs
    """
    try:
        performance_data = {
            "system_health": {
                "overall_score": 87.3,
                "availability": 99.2,
                "reliability": 94.8,
                "efficiency": 82.1
            },
            "operational_kpis": {
                "on_time_performance": 75.3,
                "average_delay": 8.7,  # minutes
                "conflict_resolution_rate": 95.4,
                "throughput_efficiency": 88.9,
                "resource_utilization": 67.2,
                "customer_satisfaction": 4.2  # out of 5
            },
            "ai_impact_metrics": {
                "schedule_optimization_success": 92.6,
                "conflict_prevention_rate": 89.1,
                "delay_reduction_achieved": 23.4,  # percentage improvement
                "automated_decisions": 78.9,  # percentage of decisions made by AI
                "prediction_accuracy": 91.3
            },
            "trends": {
                "weekly_performance": [85.2, 86.7, 88.1, 87.8, 89.2, 86.9, 87.3],
                "monthly_improvement": 3.8,  # percentage improvement over last month
                "yearly_improvement": 15.2   # percentage improvement over last year
            },
            "benchmarks": {
                "industry_average_otp": 72.1,  # on-time performance
                "industry_average_delay": 12.4,
                "our_performance_vs_industry": "+4.2% better than average"
            }
        }
        
        return APIResponse(
            status="success",
            message="Performance metrics retrieved successfully",
            data=performance_data,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")

@router.get("/realtime", response_model=APIResponse)
async def get_realtime_metrics():
    """
    Get real-time system metrics for live monitoring
    """
    try:
        current_time = datetime.now()
        
        realtime_data = {
            "timestamp": current_time.isoformat(),
            "current_metrics": {
                "active_trains": 4,
                "trains_in_transit": 2,
                "trains_at_platform": 2,
                "available_platforms": 3,
                "current_conflicts": random.randint(0, 2),
                "system_load": round(random.uniform(45, 85), 1)
            },
            "last_5_minutes": {
                "trains_departed": random.randint(0, 3),
                "trains_arrived": random.randint(0, 3),
                "delays_occurred": random.randint(0, 2),
                "conflicts_resolved": random.randint(0, 1)
            },
            "live_alerts": [
                {
                    "level": "info",
                    "message": f"Train T00{random.randint(1, 4)} departed on time",
                    "timestamp": (current_time - timedelta(minutes=2)).isoformat()
                },
                {
                    "level": "warning", 
                    "message": "Platform 2 utilization approaching capacity",
                    "timestamp": (current_time - timedelta(minutes=5)).isoformat()
                }
            ],
            "system_status": {
                "api_response_time": f"{random.uniform(45, 120):.0f}ms",
                "database_connection": "healthy",
                "ai_optimizer_status": "active",
                "websocket_connections": random.randint(8, 15)
            }
        }
        
        return APIResponse(
            status="success",
            message="Real-time metrics retrieved",
            data=realtime_data,
            timestamp=current_time.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch real-time metrics: {str(e)}")

@router.post("/export", response_model=APIResponse)
async def export_analytics_report(
    report_type: str = Query(..., description="Type of report: daily, weekly, monthly"),
    format: str = Query("json", description="Export format: json, csv, pdf")
):
    """
    Export analytics report in specified format
    """
    try:
        # Generate report data based on type
        if report_type == "daily":
            report_data = {
                "report_period": datetime.now().strftime("%Y-%m-%d"),
                "total_trains": random.randint(180, 220),
                "on_time_percentage": round(random.uniform(72, 88), 1),
                "average_delay": round(random.uniform(6, 12), 1),
                "conflicts_detected": random.randint(3, 8),
                "conflicts_resolved": random.randint(2, 7)
            }
        elif report_type == "weekly":
            report_data = {
                "report_period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
                "total_trains": random.randint(1200, 1500),
                "average_otp": round(random.uniform(74, 86), 1),
                "peak_day": "Thursday",
                "worst_day": "Monday",
                "improvement_areas": ["Platform 4 efficiency", "Weather contingency"]
            }
        else:  # monthly
            report_data = {
                "report_period": datetime.now().strftime("%Y-%m"),
                "total_trains": random.randint(5000, 6500),
                "monthly_otp": round(random.uniform(76, 84), 1),
                "trends": "Improvement in delay management",
                "ai_optimizations": random.randint(450, 650)
            }
        
        # Simulate file generation
        report_filename = f"train_analytics_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        return APIResponse(
            status="success",
            message=f"{report_type.title()} report generated successfully",
            data={
                "report_filename": report_filename,
                "format": format,
                "report_data": report_data,
                "download_url": f"/api/downloads/{report_filename}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
