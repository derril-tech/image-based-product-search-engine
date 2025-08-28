# Security Scanner Service for NSFW and Virus Detection
# Created automatically by Cursor AI (2024-12-19)

import os
import logging
import hashlib
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiofiles
import aiohttp
from PIL import Image
import numpy as np
import cv2
import io

# NSFW detection
try:
    from nudenet import NudeDetector
    NUDENET_AVAILABLE = True
except ImportError:
    NUDENET_AVAILABLE = False

# Virus scanning
try:
    import clamd
    CLAMD_AVAILABLE = True
except ImportError:
    CLAMD_AVAILABLE = False

logger = logging.getLogger(__name__)

class ScanResult(Enum):
    CLEAN = "clean"
    NSFW = "nsfw"
    VIRUS = "virus"
    SUSPICIOUS = "suspicious"
    ERROR = "error"

@dataclass
class SecurityScanResult:
    """Result of a security scan"""
    result: ScanResult
    confidence: float
    details: Dict[str, Any]
    scan_time: float
    file_hash: str
    file_size: int
    mime_type: str

class SecurityScanner:
    """Security scanner for NSFW and virus detection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enable_nsfw_detection = config.get('enable_nsfw_detection', True)
        self.enable_virus_scanning = config.get('enable_virus_scanning', True)
        self.nsfw_threshold = config.get('nsfw_threshold', 0.6)
        self.max_file_size = config.get('max_file_size', 50 * 1024 * 1024)  # 50MB
        self.allowed_mime_types = config.get('allowed_mime_types', [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'image/bmp', 'image/tiff'
        ])
        
        # Initialize NSFW detector
        self.nsfw_detector = None
        if self.enable_nsfw_detection and NUDENET_AVAILABLE:
            try:
                self.nsfw_detector = NudeDetector()
                logger.info("NSFW detector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize NSFW detector: {e}")
        
        # Initialize virus scanner
        self.clamd_client = None
        if self.enable_virus_scanning and CLAMD_AVAILABLE:
            try:
                self.clamd_client = clamd.ClamdUnixSocket()
                # Test connection
                self.clamd_client.ping()
                logger.info("Virus scanner initialized")
            except Exception as e:
                logger.error(f"Failed to initialize virus scanner: {e}")
                # Try TCP connection as fallback
                try:
                    self.clamd_client = clamd.ClamdNetworkSocket()
                    self.clamd_client.ping()
                    logger.info("Virus scanner initialized (TCP)")
                except Exception as e2:
                    logger.error(f"Failed to initialize virus scanner (TCP): {e2}")
    
    async def scan_file(self, file_data: bytes, filename: str, mime_type: str) -> SecurityScanResult:
        """Scan a file for security threats"""
        import time
        start_time = time.time()
        
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_size = len(file_data)
            
            # Basic validation
            if file_size > self.max_file_size:
                return SecurityScanResult(
                    result=ScanResult.ERROR,
                    confidence=1.0,
                    details={"error": "File too large"},
                    scan_time=time.time() - start_time,
                    file_hash=file_hash,
                    file_size=file_size,
                    mime_type=mime_type
                )
            
            if mime_type not in self.allowed_mime_types:
                return SecurityScanResult(
                    result=ScanResult.ERROR,
                    confidence=1.0,
                    details={"error": "File type not allowed"},
                    scan_time=time.time() - start_time,
                    file_hash=file_hash,
                    file_size=file_size,
                    mime_type=mime_type
                )
            
            # Run scans in parallel
            scan_tasks = []
            
            if self.enable_virus_scanning and self.clamd_client:
                scan_tasks.append(self._scan_virus(file_data, filename))
            
            if self.enable_nsfw_detection and self.nsfw_detector and mime_type.startswith('image/'):
                scan_tasks.append(self._scan_nsfw(file_data))
            
            # Wait for all scans to complete
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
            
            # Process results
            virus_result = None
            nsfw_result = None
            
            for result in scan_results:
                if isinstance(result, Exception):
                    logger.error(f"Scan error: {result}")
                    continue
                
                if result.get('type') == 'virus':
                    virus_result = result
                elif result.get('type') == 'nsfw':
                    nsfw_result = result
            
            # Determine overall result
            if virus_result and virus_result.get('detected'):
                return SecurityScanResult(
                    result=ScanResult.VIRUS,
                    confidence=virus_result.get('confidence', 1.0),
                    details=virus_result,
                    scan_time=time.time() - start_time,
                    file_hash=file_hash,
                    file_size=file_size,
                    mime_type=mime_type
                )
            
            if nsfw_result and nsfw_result.get('detected'):
                return SecurityScanResult(
                    result=ScanResult.NSFW,
                    confidence=nsfw_result.get('confidence', 1.0),
                    details=nsfw_result,
                    scan_time=time.time() - start_time,
                    file_hash=file_hash,
                    file_size=file_size,
                    mime_type=mime_type
                )
            
            # File is clean
            return SecurityScanResult(
                result=ScanResult.CLEAN,
                confidence=1.0,
                details={
                    "virus_scan": virus_result,
                    "nsfw_scan": nsfw_result
                },
                scan_time=time.time() - start_time,
                file_hash=file_hash,
                file_size=file_size,
                mime_type=mime_type
            )
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return SecurityScanResult(
                result=ScanResult.ERROR,
                confidence=0.0,
                details={"error": str(e)},
                scan_time=time.time() - start_time,
                file_hash=file_hash if 'file_hash' in locals() else "",
                file_size=len(file_data),
                mime_type=mime_type
            )
    
    async def _scan_virus(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Scan file for viruses using ClamAV"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_data)
                temp_file_path = temp_file.name
            
            try:
                # Scan file
                scan_result = self.clamd_client.scan(temp_file_path)
                
                # Check result
                if scan_result:
                    file_path, status = list(scan_result.items())[0]
                    if status[0] == 'FOUND':
                        return {
                            'type': 'virus',
                            'detected': True,
                            'confidence': 1.0,
                            'virus_name': status[1],
                            'scanner': 'clamav'
                        }
                
                return {
                    'type': 'virus',
                    'detected': False,
                    'confidence': 1.0,
                    'scanner': 'clamav'
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Virus scan failed: {e}")
            return {
                'type': 'virus',
                'detected': False,
                'confidence': 0.0,
                'error': str(e),
                'scanner': 'clamav'
            }
    
    async def _scan_nsfw(self, file_data: bytes) -> Dict[str, Any]:
        """Scan image for NSFW content"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temporary file (NudeDetector requires file path)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                image.save(temp_file, 'JPEG')
                temp_file_path = temp_file.name
            
            try:
                # Detect NSFW content
                detections = self.nsfw_detector.detect(temp_file_path)
                
                # Calculate NSFW score
                nsfw_score = 0.0
                nsfw_details = []
                
                for detection in detections:
                    if detection['class'] in ['FEMALE_GENITALIA', 'MALE_GENITALIA', 'FEMALE_BREAST', 'MALE_BREAST']:
                        nsfw_score += detection['score']
                        nsfw_details.append({
                            'class': detection['class'],
                            'score': detection['score'],
                            'bbox': detection['bbox']
                        })
                
                # Normalize score
                nsfw_score = min(nsfw_score, 1.0)
                
                return {
                    'type': 'nsfw',
                    'detected': nsfw_score > self.nsfw_threshold,
                    'confidence': nsfw_score,
                    'score': nsfw_score,
                    'threshold': self.nsfw_threshold,
                    'details': nsfw_details,
                    'scanner': 'nudenet'
                }
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"NSFW scan failed: {e}")
            return {
                'type': 'nsfw',
                'detected': False,
                'confidence': 0.0,
                'error': str(e),
                'scanner': 'nudenet'
            }
    
    async def scan_batch(self, files: List[Tuple[bytes, str, str]]) -> List[SecurityScanResult]:
        """Scan multiple files in batch"""
        tasks = []
        for file_data, filename, mime_type in files:
            task = self.scan_file(file_data, filename, mime_type)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    def is_file_safe(self, scan_result: SecurityScanResult) -> bool:
        """Check if a scan result indicates the file is safe"""
        return scan_result.result == ScanResult.CLEAN
    
    def get_scan_summary(self, scan_result: SecurityScanResult) -> Dict[str, Any]:
        """Get a summary of the scan result"""
        return {
            'safe': self.is_file_safe(scan_result),
            'result': scan_result.result.value,
            'confidence': scan_result.confidence,
            'file_size': scan_result.file_size,
            'mime_type': scan_result.mime_type,
            'scan_time': scan_result.scan_time,
            'file_hash': scan_result.file_hash
        }
    
    def update_signatures(self) -> bool:
        """Update virus signatures"""
        if not self.clamd_client:
            return False
        
        try:
            # Reload virus database
            self.clamd_client.reload()
            logger.info("Virus signatures updated")
            return True
        except Exception as e:
            logger.error(f"Failed to update virus signatures: {e}")
            return False
    
    def get_scanner_status(self) -> Dict[str, Any]:
        """Get status of all scanners"""
        return {
            'nsfw_detection': {
                'enabled': self.enable_nsfw_detection,
                'available': NUDENET_AVAILABLE,
                'initialized': self.nsfw_detector is not None
            },
            'virus_scanning': {
                'enabled': self.enable_virus_scanning,
                'available': CLAMD_AVAILABLE,
                'initialized': self.clamd_client is not None
            },
            'config': {
                'nsfw_threshold': self.nsfw_threshold,
                'max_file_size': self.max_file_size,
                'allowed_mime_types': self.allowed_mime_types
            }
        }

class SecurityPolicy:
    """Security policy enforcement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.block_nsfw = config.get('block_nsfw', True)
        self.block_virus = config.get('block_virus', True)
        self.quarantine_suspicious = config.get('quarantine_suspicious', True)
        self.allow_list = config.get('allow_list', [])
        self.block_list = config.get('block_list', [])
    
    def evaluate_scan_result(self, scan_result: SecurityScanResult) -> Dict[str, Any]:
        """Evaluate scan result against security policy"""
        action = 'allow'
        reason = 'clean'
        
        # Check file hash against allow/block lists
        if scan_result.file_hash in self.allow_list:
            action = 'allow'
            reason = 'whitelisted'
        elif scan_result.file_hash in self.block_list:
            action = 'block'
            reason = 'blacklisted'
        elif scan_result.result == ScanResult.NSFW and self.block_nsfw:
            action = 'block'
            reason = 'nsfw_content'
        elif scan_result.result == ScanResult.VIRUS and self.block_virus:
            action = 'block'
            reason = 'virus_detected'
        elif scan_result.result == ScanResult.SUSPICIOUS and self.quarantine_suspicious:
            action = 'quarantine'
            reason = 'suspicious_content'
        elif scan_result.result == ScanResult.ERROR:
            action = 'block'
            reason = 'scan_error'
        
        return {
            'action': action,
            'reason': reason,
            'scan_result': scan_result.result.value,
            'confidence': scan_result.confidence,
            'details': scan_result.details
        }
