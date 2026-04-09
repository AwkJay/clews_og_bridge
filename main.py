"""
CLEWS → OG-Core semantic bridge API. 
Accepts CLEWS output CSVs, runs the validated mapping pipeline, 
returns OG-Core-compatible parameters with full mapping trace.
"""
from __future__ import annotations

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import yaml
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add src/ to sys.path at startup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from clews_og_bridge.pipeline import Pipeline
from clews_og_bridge.config import MappingConfig

app = FastAPI(title="CLEWS-OG-Core Bridge API", version="0.1.0")

# CORS for demo purposes only - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory run history
RUN_HISTORY: List[Dict[str, Any]] = []

def add_to_history(run_id: str, scenario: str, country: Optional[str], status: str):
    RUN_HISTORY.append({
        "run_id": run_id,
        "scenario": scenario,
        "country": country,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": status
    })
    RUN_HISTORY[:] = RUN_HISTORY[-200:]


@app.get("/")
def get_root():
    return {"service":"clews-og-bridge","docs":"/docs","health":"/health"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "clews-og-bridge", "version": "0.1.0"}


@app.get("/schema")
def get_schema():
    config_path = Path(__file__).parent / "configs" / "mapping.yaml"
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading schema: {e}")


@app.post("/transform")
async def transform(
    scenario: str = Form(...),
    run_id: str = Form(...),
    country: Optional[str] = Form(None),
    total_discounted_cost: UploadFile = File(...),
    total_annual_technology_activity: UploadFile = File(...),
    annual_emissions: UploadFile = File(...)
):
    temp_dir = ""
    try:
        temp_dir = tempfile.mkdtemp()
        
        # Save files
        files_to_save = [
            (total_discounted_cost, "TotalDiscountedCost.csv"),
            (total_annual_technology_activity, "TotalAnnualTechnologyActivity.csv"),
            (annual_emissions, "AnnualEmissions.csv")
        ]
        
        for file_obj, filename in files_to_save:
            if not file_obj or not file_obj.filename:
                raise HTTPException(status_code=422, detail=f"Missing file: {filename}")
                
            file_path = os.path.join(temp_dir, filename)
            content = await file_obj.read()
            with open(file_path, "wb") as f:
                f.write(content)
        
        # Load configs
        config_path = Path(__file__).parent / "configs" / "mapping.yaml"
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)
        config = MappingConfig.model_validate(config_dict)
        
        # Output path (temp file just for pipeline, though pipeline returns model)
        output_path = Path(temp_dir) / "output.json"
        
        # Run pipeline
        pipeline = Pipeline(config)
        model = pipeline.run(
            input_dir=Path(temp_dir),
            output_path=output_path,
            scenario=scenario,
            run_id=run_id,
            country=country
        )
        
        add_to_history(run_id, scenario, country, "success")
        return model.model_dump(mode="json")
        
    except HTTPException as e:
        add_to_history(run_id, scenario, country, "error")
        raise e
    except Exception as e:
        add_to_history(run_id, scenario, country, "error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.get("/history")
def get_history():
    return RUN_HISTORY[-50:]
