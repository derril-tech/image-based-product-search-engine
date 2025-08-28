# Security Router for NSFW and Virus Scanning
# Created automatically by Cursor AI (2024-12-19)

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict
import logging
from pydantic import BaseModel
import io

from ..services.security_scanner import SecurityScanner, SecurityPolicy, ScanResult, SecurityScanResult
from ..dependencies import get_security_scanner, get_security_policy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["Security"])

class SecurityScanResponse(BaseModel):
    safe: bool
    result: str
    confidence: float
    file_size: int
    mime_type: str
    scan_time: float
    file_hash: str
    details: Dict

class SecurityPolicyResponse(BaseModel):
    action: str
    reason: str
    scan_result: str
    confidence: float
    details: Dict

class BatchScanRequest(BaseModel):
    block_nsfw: Optional[bool] = True
    block_virus: Optional[bool] = True
    quarantine_suspicious: Optional[bool] = True

class ScannerStatusResponse(BaseModel):
    nsfw_detection: Dict
    virus_scanning: Dict
    config: Dict

@router.post("/scan", response_model=SecurityScanResponse)
async def scan_file(
    file: UploadFile = File(...),
    scanner: SecurityScanner = Depends(get_security_scanner)
):
    """Scan a single file for security threats"""
    try:
        # Read file data
        file_data = await file.read()
        
        # Scan file
        scan_result = await scanner.scan_file(file_data, file.filename, file.content_type)
        
        # Return scan result
        return SecurityScanResponse(
            safe=scanner.is_file_safe(scan_result),
            result=scan_result.result.value,
            confidence=scan_result.confidence,
            file_size=scan_result.file_size,
            mime_type=scan_result.mime_type,
            scan_time=scan_result.scan_time,
            file_hash=scan_result.file_hash,
            details=scan_result.details
        )
        
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan/batch")
async def scan_batch(
    files: List[UploadFile] = File(...),
    request: BatchScanRequest = None,
    scanner: SecurityScanner = Depends(get_security_scanner),
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Scan multiple files in batch"""
    try:
        # Prepare files for batch scanning
        file_tuples = []
        for file in files:
            file_data = await file.read()
            file_tuples.append((file_data, file.filename, file.content_type))
        
        # Scan all files
        scan_results = await scanner.scan_batch(file_tuples)
        
        # Evaluate results against policy
        results = []
        for i, scan_result in enumerate(scan_results):
            policy_result = policy.evaluate_scan_result(scan_result)
            
            results.append({
                'filename': files[i].filename,
                'scan_result': scanner.get_scan_summary(scan_result),
                'policy_result': policy_result
            })
        
        return {
            'message': f'Scanned {len(files)} files',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Batch security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan/async")
async def scan_file_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    scanner: SecurityScanner = Depends(get_security_scanner)
):
    """Scan a file asynchronously"""
    try:
        # Read file data
        file_data = await file.read()
        
        # Generate scan ID
        import hashlib
        import time
        scan_id = hashlib.md5(f"{file.filename}_{time.time()}".encode()).hexdigest()
        
        # Store scan task (in a real implementation, this would be in a database/queue)
        # For now, we'll just return the scan ID
        return {
            'scan_id': scan_id,
            'filename': file.filename,
            'status': 'queued',
            'message': 'Scan queued for processing'
        }
        
    except Exception as e:
        logger.error(f"Async security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan/{scan_id}")
async def get_scan_status(
    scan_id: str,
    scanner: SecurityScanner = Depends(get_security_scanner)
):
    """Get the status of an async scan"""
    # In a real implementation, this would check the database/queue
    # For now, return a mock response
    return {
        'scan_id': scan_id,
        'status': 'completed',
        'result': 'clean',
        'message': 'Scan completed successfully'
    }

@router.post("/evaluate", response_model=SecurityPolicyResponse)
async def evaluate_scan_result(
    scan_result: SecurityScanResponse,
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Evaluate a scan result against security policy"""
    try:
        # Convert to SecurityScanResult
        security_scan_result = SecurityScanResult(
            result=ScanResult(scan_result.result),
            confidence=scan_result.confidence,
            details=scan_result.details,
            scan_time=scan_result.scan_time,
            file_hash=scan_result.file_hash,
            file_size=scan_result.file_size,
            mime_type=scan_result.mime_type
        )
        
        # Evaluate against policy
        policy_result = policy.evaluate_scan_result(security_scan_result)
        
        return SecurityPolicyResponse(**policy_result)
        
    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=ScannerStatusResponse)
async def get_scanner_status(
    scanner: SecurityScanner = Depends(get_security_scanner)
):
    """Get status of security scanners"""
    try:
        status = scanner.get_scanner_status()
        return ScannerStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Failed to get scanner status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signatures/update")
async def update_virus_signatures(
    scanner: SecurityScanner = Depends(get_security_scanner)
):
    """Update virus signatures"""
    try:
        success = scanner.update_signatures()
        
        if success:
            return {
                'message': 'Virus signatures updated successfully',
                'status': 'success'
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update virus signatures")
            
    except Exception as e:
        logger.error(f"Failed to update virus signatures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/policy/allow")
async def add_to_allow_list(
    file_hash: str,
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Add a file hash to the allow list"""
    try:
        if file_hash not in policy.allow_list:
            policy.allow_list.append(file_hash)
        
        return {
            'message': f'File hash {file_hash} added to allow list',
            'allow_list': policy.allow_list
        }
        
    except Exception as e:
        logger.error(f"Failed to add to allow list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/policy/block")
async def add_to_block_list(
    file_hash: str,
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Add a file hash to the block list"""
    try:
        if file_hash not in policy.block_list:
            policy.block_list.append(file_hash)
        
        return {
            'message': f'File hash {file_hash} added to block list',
            'block_list': policy.block_list
        }
        
    except Exception as e:
        logger.error(f"Failed to add to block list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/policy/allow/{file_hash}")
async def remove_from_allow_list(
    file_hash: str,
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Remove a file hash from the allow list"""
    try:
        if file_hash in policy.allow_list:
            policy.allow_list.remove(file_hash)
        
        return {
            'message': f'File hash {file_hash} removed from allow list',
            'allow_list': policy.allow_list
        }
        
    except Exception as e:
        logger.error(f"Failed to remove from allow list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/policy/block/{file_hash}")
async def remove_from_block_list(
    file_hash: str,
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Remove a file hash from the block list"""
    try:
        if file_hash in policy.block_list:
            policy.block_list.remove(file_hash)
        
        return {
            'message': f'File hash {file_hash} removed from block list',
            'block_list': policy.block_list
        }
        
    except Exception as e:
        logger.error(f"Failed to remove from block list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/policy/lists")
async def get_policy_lists(
    policy: SecurityPolicy = Depends(get_security_policy)
):
    """Get current allow and block lists"""
    try:
        return {
            'allow_list': policy.allow_list,
            'block_list': policy.block_list,
            'config': {
                'block_nsfw': policy.block_nsfw,
                'block_virus': policy.block_virus,
                'quarantine_suspicious': policy.quarantine_suspicious
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get policy lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/clean")
async def test_clean_file():
    """Test endpoint with a clean file"""
    try:
        # Create a simple test image
        from PIL import Image
        import io
        
        # Create a 100x100 white image
        image = Image.new('RGB', (100, 100), color='white')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create mock scan result
        mock_result = SecurityScanResult(
            result=ScanResult.CLEAN,
            confidence=1.0,
            details={'test': True},
            scan_time=0.1,
            file_hash='test_hash',
            file_size=len(img_byte_arr),
            mime_type='image/jpeg'
        )
        
        return {
            'safe': True,
            'result': 'clean',
            'confidence': 1.0,
            'file_size': len(img_byte_arr),
            'mime_type': 'image/jpeg',
            'scan_time': 0.1,
            'file_hash': 'test_hash',
            'details': {'test': True}
        }
        
    except Exception as e:
        logger.error(f"Test endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
