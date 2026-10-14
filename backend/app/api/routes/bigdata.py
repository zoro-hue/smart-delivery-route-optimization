"""
Big Data Pipeline Endpoints for ROUTE/IQ.
Provides observability and control for the PySpark / Parquet batch ETL engine.
"""

from fastapi import APIRouter, HTTPException
from app.services.bigdata_pipeline import bigdata_pipeline, get_pyspark_schemas

router = APIRouter(prefix="/bigdata", tags=["Big Data Pipeline"])


@router.get("/status")
async def get_pipeline_status():
    """Retrieve telemetry, dataset row counts, Parquet artifacts, and execution metrics."""
    status = bigdata_pipeline.get_status()
    schemas = get_pyspark_schemas()
    return {
        "status": "success",
        "pipeline": status,
        "schemas_defined": list(schemas.keys()),
    }


@router.post("/run-etl")
async def trigger_pipeline_etl():
    """Trigger the Big Data batch ETL pipeline to curate datasets into Parquet."""
    try:
        updated = bigdata_pipeline.run_pipeline()
        return {
            "status": "success",
            "message": "Big Data ETL executed successfully.",
            "pipeline": updated,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")
