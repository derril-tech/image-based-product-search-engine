# Created automatically by Cursor AI (2024-12-19)

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from decimal import Decimal
from ..services.billing_service import (
    BillingService, PlanType, UsageType, BillingStatus,
    TenantPlan, UsageRecord, BillingPeriod
)
from ..dependencies import get_billing_service

router = APIRouter(prefix="/billing", tags=["Billing"])


class CreateTenantRequest(BaseModel):
    tenant_id: str
    plan_type: PlanType = PlanType.FREE


class UpdatePlanRequest(BaseModel):
    plan_type: PlanType


class UsageRecordRequest(BaseModel):
    usage_type: UsageType
    quantity: int = Field(default=1, ge=1)
    metadata: Optional[Dict[str, Any]] = None


class BillingPeriodRequest(BaseModel):
    period_start: datetime
    period_end: datetime


class TenantPlanResponse(BaseModel):
    tenant_id: str
    plan_type: PlanType
    status: BillingStatus
    current_period_start: datetime
    current_period_end: datetime
    limits: Dict[str, Any]
    pricing: Dict[str, Any]
    auto_renew: bool
    trial_end: Optional[datetime] = None


class UsageSummaryResponse(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    usage: Dict[str, int]
    limits: Dict[str, int]
    utilization: Dict[str, float]


class BillingPeriodResponse(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    usage: Dict[str, int]
    charges: Dict[str, str]
    total_amount: str
    status: str


class PlanInfoResponse(BaseModel):
    plan_type: PlanType
    limits: Dict[str, Any]
    pricing: Dict[str, Any]
    features: List[str]


@router.post("/tenants", response_model=TenantPlanResponse)
async def create_tenant(
    request: CreateTenantRequest,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Create a new tenant with the specified plan."""
    try:
        tenant_plan = await billing_service.create_tenant(
            tenant_id=request.tenant_id,
            plan_type=request.plan_type
        )
        
        return TenantPlanResponse(
            tenant_id=tenant_plan.tenant_id,
            plan_type=tenant_plan.plan_type,
            status=tenant_plan.status,
            current_period_start=tenant_plan.current_period_start,
            current_period_end=tenant_plan.current_period_end,
            limits={
                "search_queries_per_month": tenant_plan.limits.search_queries_per_month,
                "image_uploads_per_month": tenant_plan.limits.image_uploads_per_month,
                "storage_gb": tenant_plan.limits.storage_gb,
                "api_calls_per_month": tenant_plan.limits.api_calls_per_month,
                "embedding_generation_per_month": tenant_plan.limits.embedding_generation_per_month,
                "index_rebuilds_per_month": tenant_plan.limits.index_rebuilds_per_month,
                "max_collections": tenant_plan.limits.max_collections,
                "max_users": tenant_plan.limits.max_users,
                "support_level": tenant_plan.limits.support_level
            },
            pricing={
                "monthly_price": str(tenant_plan.pricing.monthly_price),
                "yearly_price": str(tenant_plan.pricing.yearly_price),
                "overage_rates": {k: str(v) for k, v in tenant_plan.pricing.overage_rates.items()}
            },
            auto_renew=tenant_plan.auto_renew,
            trial_end=tenant_plan.trial_end
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")


@router.get("/tenants/{tenant_id}", response_model=TenantPlanResponse)
async def get_tenant_plan(
    tenant_id: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Get tenant plan information."""
    try:
        tenant_plan = await billing_service.get_tenant_plan(tenant_id)
        if not tenant_plan:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        return TenantPlanResponse(
            tenant_id=tenant_plan.tenant_id,
            plan_type=tenant_plan.plan_type,
            status=tenant_plan.status,
            current_period_start=tenant_plan.current_period_start,
            current_period_end=tenant_plan.current_period_end,
            limits={
                "search_queries_per_month": tenant_plan.limits.search_queries_per_month,
                "image_uploads_per_month": tenant_plan.limits.image_uploads_per_month,
                "storage_gb": tenant_plan.limits.storage_gb,
                "api_calls_per_month": tenant_plan.limits.api_calls_per_month,
                "embedding_generation_per_month": tenant_plan.limits.embedding_generation_per_month,
                "index_rebuilds_per_month": tenant_plan.limits.index_rebuilds_per_month,
                "max_collections": tenant_plan.limits.max_collections,
                "max_users": tenant_plan.limits.max_users,
                "support_level": tenant_plan.limits.support_level
            },
            pricing={
                "monthly_price": str(tenant_plan.pricing.monthly_price),
                "yearly_price": str(tenant_plan.pricing.yearly_price),
                "overage_rates": {k: str(v) for k, v in tenant_plan.pricing.overage_rates.items()}
            },
            auto_renew=tenant_plan.auto_renew,
            trial_end=tenant_plan.trial_end
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tenant plan: {str(e)}")


@router.put("/tenants/{tenant_id}/plan", response_model=TenantPlanResponse)
async def update_tenant_plan(
    tenant_id: str,
    request: UpdatePlanRequest,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Update tenant plan."""
    try:
        tenant_plan = await billing_service.update_tenant_plan(
            tenant_id=tenant_id,
            plan_type=request.plan_type
        )
        
        return TenantPlanResponse(
            tenant_id=tenant_plan.tenant_id,
            plan_type=tenant_plan.plan_type,
            status=tenant_plan.status,
            current_period_start=tenant_plan.current_period_start,
            current_period_end=tenant_plan.current_period_end,
            limits={
                "search_queries_per_month": tenant_plan.limits.search_queries_per_month,
                "image_uploads_per_month": tenant_plan.limits.image_uploads_per_month,
                "storage_gb": tenant_plan.limits.storage_gb,
                "api_calls_per_month": tenant_plan.limits.api_calls_per_month,
                "embedding_generation_per_month": tenant_plan.limits.embedding_generation_per_month,
                "index_rebuilds_per_month": tenant_plan.limits.index_rebuilds_per_month,
                "max_collections": tenant_plan.limits.max_collections,
                "max_users": tenant_plan.limits.max_users,
                "support_level": tenant_plan.limits.support_level
            },
            pricing={
                "monthly_price": str(tenant_plan.pricing.monthly_price),
                "yearly_price": str(tenant_plan.pricing.yearly_price),
                "overage_rates": {k: str(v) for k, v in tenant_plan.pricing.overage_rates.items()}
            },
            auto_renew=tenant_plan.auto_renew,
            trial_end=tenant_plan.trial_end
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tenant plan: {str(e)}")


@router.post("/tenants/{tenant_id}/usage")
async def record_usage(
    tenant_id: str,
    request: UsageRecordRequest,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Record usage for a tenant."""
    try:
        success = await billing_service.record_usage(
            tenant_id=tenant_id,
            usage_type=request.usage_type,
            quantity=request.quantity,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to record usage")
        
        return {"message": "Usage recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record usage: {str(e)}")


@router.get("/tenants/{tenant_id}/usage", response_model=UsageSummaryResponse)
async def get_usage_summary(
    tenant_id: str,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    billing_service: BillingService = Depends(get_billing_service)
):
    """Get usage summary for a tenant."""
    try:
        # Default to current month if not specified
        if not period_start:
            current_time = datetime.utcnow()
            period_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if not period_end:
            period_end = datetime.utcnow()
        
        usage_summary = await billing_service.get_usage_summary(
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end
        )
        
        # Get tenant plan for limits
        tenant_plan = await billing_service.get_tenant_plan(tenant_id)
        if not tenant_plan:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        limits = {
            "search_queries_per_month": tenant_plan.limits.search_queries_per_month,
            "image_uploads_per_month": tenant_plan.limits.image_uploads_per_month,
            "storage_gb": tenant_plan.limits.storage_gb,
            "api_calls_per_month": tenant_plan.limits.api_calls_per_month,
            "embedding_generation_per_month": tenant_plan.limits.embedding_generation_per_month,
            "index_rebuilds_per_month": tenant_plan.limits.index_rebuilds_per_month
        }
        
        # Calculate utilization percentages
        utilization = {}
        for usage_type, current_usage in usage_summary.items():
            limit_key = f"{usage_type}_per_month"
            limit_value = limits.get(limit_key, 0)
            if limit_value > 0:
                utilization[usage_type] = (current_usage / limit_value) * 100
            else:
                utilization[usage_type] = 0.0
        
        return UsageSummaryResponse(
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            usage=usage_summary,
            limits=limits,
            utilization=utilization
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage summary: {str(e)}")


@router.post("/tenants/{tenant_id}/billing", response_model=BillingPeriodResponse)
async def calculate_billing(
    tenant_id: str,
    request: BillingPeriodRequest,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Calculate billing for a tenant in a given period."""
    try:
        billing_period = await billing_service.calculate_billing(
            tenant_id=tenant_id,
            period_start=request.period_start,
            period_end=request.period_end
        )
        
        return BillingPeriodResponse(
            tenant_id=billing_period.tenant_id,
            period_start=billing_period.period_start,
            period_end=billing_period.period_end,
            usage=billing_period.usage,
            charges={k: str(v) for k, v in billing_period.charges.items()},
            total_amount=str(billing_period.total_amount),
            status=billing_period.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate billing: {str(e)}")


@router.get("/tenants/{tenant_id}/limits/check")
async def check_usage_limits(
    tenant_id: str,
    usage_type: UsageType,
    quantity: int = Query(default=1, ge=1),
    billing_service: BillingService = Depends(get_billing_service)
):
    """Check if usage would exceed limits."""
    try:
        within_limits = await billing_service.check_usage_limits(
            tenant_id=tenant_id,
            usage_type=usage_type,
            quantity=quantity
        )
        
        return {
            "tenant_id": tenant_id,
            "usage_type": usage_type.value,
            "quantity": quantity,
            "within_limits": within_limits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check usage limits: {str(e)}")


@router.get("/plans", response_model=List[PlanInfoResponse])
async def get_available_plans(
    billing_service: BillingService = Depends(get_billing_service)
):
    """Get available plans and their features."""
    try:
        plans = []
        for plan_type, plan_config in billing_service.plans.items():
            features = []
            
            # Add features based on plan type
            if plan_type == PlanType.FREE:
                features = ["Basic search", "Limited uploads", "Community support"]
            elif plan_type == PlanType.BASIC:
                features = ["Advanced search", "More uploads", "Email support", "Basic analytics"]
            elif plan_type == PlanType.PRO:
                features = ["Premium search", "High volume uploads", "Priority support", "Advanced analytics", "Custom models"]
            elif plan_type == PlanType.ENTERPRISE:
                features = ["Enterprise search", "Unlimited uploads", "Dedicated support", "Full analytics", "Custom models", "SLA guarantee"]
            
            plans.append(PlanInfoResponse(
                plan_type=plan_type,
                limits={
                    "search_queries_per_month": plan_config["limits"].search_queries_per_month,
                    "image_uploads_per_month": plan_config["limits"].image_uploads_per_month,
                    "storage_gb": plan_config["limits"].storage_gb,
                    "api_calls_per_month": plan_config["limits"].api_calls_per_month,
                    "embedding_generation_per_month": plan_config["limits"].embedding_generation_per_month,
                    "index_rebuilds_per_month": plan_config["limits"].index_rebuilds_per_month,
                    "max_collections": plan_config["limits"].max_collections,
                    "max_users": plan_config["limits"].max_users,
                    "support_level": plan_config["limits"].support_level
                },
                pricing={
                    "monthly_price": str(plan_config["pricing"].monthly_price),
                    "yearly_price": str(plan_config["pricing"].yearly_price),
                    "overage_rates": {k: str(v) for k, v in plan_config["pricing"].overage_rates.items()}
                },
                features=features
            ))
        
        return plans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available plans: {str(e)}")


@router.get("/usage/types")
async def get_usage_types():
    """Get available usage types."""
    return {
        "usage_types": [
            {
                "name": "search_queries",
                "description": "Number of search queries performed"
            },
            {
                "name": "image_uploads",
                "description": "Number of images uploaded and processed"
            },
            {
                "name": "storage_gb",
                "description": "Storage usage in gigabytes"
            },
            {
                "name": "api_calls",
                "description": "Number of API calls made"
            },
            {
                "name": "embedding_generation",
                "description": "Number of embeddings generated"
            },
            {
                "name": "index_rebuilds",
                "description": "Number of index rebuilds performed"
            }
        ]
    }
