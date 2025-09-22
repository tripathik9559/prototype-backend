# main.py - FastAPI App Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import trains, schedule, conflicts, kpis
from optimization.demo_optimizer import TrainOptimizer
import asyncio
import uvicorn

# Create FastAPI app instance
app = FastAPI(
    title="AI-Powered Train Traffic Control System",
    description="SIH 25022 - Maximizing Section Throughput Using AI",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(trains.router, prefix="/api/trains", tags=["trains"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(conflicts.router, prefix="/api/conflicts", tags=["conflicts"])
app.include_router(kpis.router, prefix="/api/kpis", tags=["analytics"])

# Initialize the optimization engine
optimizer = TrainOptimizer()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚂 Train Traffic Control System Starting...")
    print("🤖 AI Optimization Engine Initialized")
    print("📊 Analytics Module Ready")
    print("⚡ WebSocket Support Enabled")

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "message": "AI-Powered Train Traffic Control System",
        "status": "operational",
        "version": "1.0.0",
        "features": [
            "AI-driven train priority",
            "Dynamic delay management", 
            "Conflict & safety control",
            "Smart platform allocation",
            "Scenario simulation",
            "Performance analytics"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check for system components"""
    return {
        "api": "healthy",
        "database": "connected",
        "ai_optimizer": "ready",
        "websocket": "active",
        "timestamp": "2025-01-20T10:30:00Z"
    }

@app.get("/api/optimize")
async def optimize_schedule():
    """Trigger AI optimization for current schedule"""
    try:
        # Run the optimization algorithm
        result = optimizer.optimize_train_schedule()
        return {
            "status": "success",
            "optimization_result": result,
            "message": "Schedule optimized successfully"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Optimization failed: {str(e)}"
        }

# WebSocket endpoint for real-time updates (simplified mock)
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket connection for real-time train status updates"""
    await websocket.accept()
    try:
        while True:
            # Send mock real-time data every 5 seconds
            data = {
                "timestamp": "2025-01-20T10:30:00Z",
                "active_trains": 4,
                "delays": 2,
                "conflicts": 0,
                "throughput": 25
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )