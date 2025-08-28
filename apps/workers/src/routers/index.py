"""FastAPI router for index management endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import json

from ..models.index_models import (
    IndexRequest, IndexResponse, IndexJobStatus, UpsertRequest, UpsertResponse,
    DeleteRequest, RebuildRequest, RebuildResponse, CollectionInfo, IndexStats,
    SearchRequest, SearchResponse, IndexHealth, BackupRequest, RestoreRequest
)
from ..services.index_service import IndexService

router = APIRouter(prefix="/index", tags=["Index Management"])

# Initialize service
index_service = IndexService()

@router.post("/create", response_model=IndexResponse)
async def create_index(request: IndexRequest):
    """Create a new vector index."""
    try:
        job_id = await index_service.create_index(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(index_service.process_index_creation(job_id))
        
        return IndexResponse(
            job_id=job_id,
            status="started",
            message="Index creation started successfully",
            collection_name=request.collection_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upsert", response_model=UpsertResponse)
async def upsert_vectors(request: UpsertRequest):
    """Upsert vectors into an index."""
    try:
        job_id = await index_service.upsert_vectors(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(index_service.process_upsert(job_id))
        
        return UpsertResponse(
            job_id=job_id,
            status="started",
            message="Upsert started successfully",
            total_vectors=len(request.vectors),
            collection_name=request.collection_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete")
async def delete_vectors(request: DeleteRequest):
    """Delete vectors from an index."""
    try:
        job_id = await index_service.delete_vectors(request)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "message": "Vectors deleted successfully",
            "total_ids": len(request.ids),
            "collection_name": request.collection_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild", response_model=RebuildResponse)
async def rebuild_index(request: RebuildRequest):
    """Rebuild an existing index."""
    try:
        job_id = await index_service.rebuild_index(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(index_service.process_rebuild(job_id))
        
        return RebuildResponse(
            job_id=job_id,
            status="started",
            message="Index rebuild started successfully",
            collection_name=request.collection_name,
            old_index_type=None,  # Would get from collection
            new_index_type=request.index_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search_vectors(request: SearchRequest):
    """Search vectors in an index."""
    try:
        return await index_service.search_vectors(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=IndexJobStatus)
async def get_index_status(job_id: str):
    """Get the status of an index job."""
    try:
        return await index_service.get_index_status(job_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upsert-status/{job_id}")
async def get_upsert_status(job_id: str):
    """Get the status of an upsert job."""
    try:
        return await index_service.get_upsert_status(job_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    """List all collections."""
    try:
        return await index_service.list_collections()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    """Get information about a specific collection."""
    try:
        return await index_service.get_collection_info(collection_name)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{collection_name}", response_model=IndexStats)
async def get_index_stats(collection_name: str):
    """Get statistics for an index."""
    try:
        return await index_service.get_index_stats(collection_name)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/{collection_name}", response_model=IndexHealth)
async def get_index_health(collection_name: str):
    """Get health status of an index."""
    try:
        return await index_service.get_index_health(collection_name)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup")
async def backup_index(request: BackupRequest):
    """Backup an index."""
    try:
        job_id = await index_service.backup_index(request)
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Backup started successfully",
            "backup_path": request.backup_path,
            "collection_name": request.collection_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_index(request: RestoreRequest):
    """Restore an index from backup."""
    try:
        job_id = await index_service.restore_index(request)
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Restore started successfully",
            "collection_name": request.collection_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel an ongoing job."""
    try:
        await index_service.cancel_job(job_id)
        return {"message": "Job cancelled successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{collection_name}")
async def drop_collection(collection_name: str):
    """Drop a collection."""
    try:
        await index_service.drop_collection(collection_name)
        return {"message": f"Collection {collection_name} dropped successfully"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/{collection_name}")
async def optimize_index(collection_name: str):
    """Optimize an index for better performance."""
    try:
        job_id = await index_service.optimize_index(collection_name)
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Index optimization started successfully",
            "collection_name": collection_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_jobs():
    """List all active jobs."""
    try:
        index_jobs = list(index_service.active_jobs.values())
        upsert_jobs = list(index_service.upsert_jobs.values())
        
        return {
            "index_jobs": len(index_jobs),
            "upsert_jobs": len(upsert_jobs),
            "total_jobs": len(index_jobs) + len(upsert_jobs),
            "jobs": {
                "index": index_jobs,
                "upsert": upsert_jobs
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{collection_name}")
async def list_collection_jobs(collection_name: str):
    """List all jobs for a specific collection."""
    try:
        index_jobs = [
            job for job in index_service.active_jobs.values() 
            if job.collection_name == collection_name
        ]
        upsert_jobs = [
            job for job in index_service.upsert_jobs.values() 
            if job.collection_name == collection_name
        ]
        
        return {
            "collection_name": collection_name,
            "index_jobs": len(index_jobs),
            "upsert_jobs": len(upsert_jobs),
            "total_jobs": len(index_jobs) + len(upsert_jobs),
            "jobs": {
                "index": index_jobs,
                "upsert": upsert_jobs
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configs")
async def get_index_configs():
    """Get available index configurations."""
    configs = {
        "FLAT": {
            "description": "Exact search, slow but accurate",
            "params": ["nlist", "m", "efConstruction"],
            "best_for": "Small datasets, high accuracy"
        },
        "IVF_FLAT": {
            "description": "Inverted file index with flat vectors",
            "params": ["nlist"],
            "best_for": "Medium datasets, good accuracy"
        },
        "IVF_SQ8": {
            "description": "Inverted file index with scalar quantization",
            "params": ["nlist"],
            "best_for": "Large datasets, memory efficient"
        },
        "IVF_PQ": {
            "description": "Inverted file index with product quantization",
            "params": ["nlist", "m", "nbits"],
            "best_for": "Very large datasets, high compression"
        },
        "HNSW": {
            "description": "Hierarchical Navigable Small World graph",
            "params": ["M", "efConstruction"],
            "best_for": "Fast approximate search"
        }
    }
    
    return {
        "index_types": configs,
        "metric_types": {
            "L2": "Euclidean distance",
            "IP": "Inner product (for normalized vectors)",
            "COSINE": "Cosine similarity"
        }
    }

@router.post("/batch-upsert")
async def batch_upsert(
    collection_name: str,
    vectors: str,  # JSON string of vectors
    ids: str,      # JSON string of IDs
    metadata: Optional[str] = None,  # JSON string of metadata
    batch_size: int = Query(1000, ge=1, le=10000)
):
    """Batch upsert vectors with JSON input."""
    try:
        # Parse JSON inputs
        vectors_list = json.loads(vectors)
        ids_list = json.loads(ids)
        metadata_list = json.loads(metadata) if metadata else None
        
        request = UpsertRequest(
            collection_name=collection_name,
            organization_id="",  # Would come from context
            vectors=vectors_list,
            ids=ids_list,
            metadata=metadata_list,
            batch_size=batch_size
        )
        
        job_id = await index_service.upsert_vectors(request)
        
        # Start processing in background
        import asyncio
        asyncio.create_task(index_service.process_upsert(job_id))
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Batch upsert started successfully",
            "total_vectors": len(vectors_list),
            "collection_name": collection_name
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-search")
async def batch_search(
    collection_name: str,
    query_vectors: str,  # JSON string of query vectors
    top_k: int = Query(10, ge=1, le=1000),
    search_params: Optional[str] = None,  # JSON string of search params
    filter_expr: Optional[str] = None
):
    """Batch search vectors with JSON input."""
    try:
        # Parse JSON inputs
        vectors_list = json.loads(query_vectors)
        params_dict = json.loads(search_params) if search_params else {}
        
        request = SearchRequest(
            collection_name=collection_name,
            organization_id="",  # Would come from context
            query_vectors=vectors_list,
            top_k=top_k,
            search_params=params_dict,
            filter_expr=filter_expr
        )
        
        return await index_service.search_vectors(request)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
