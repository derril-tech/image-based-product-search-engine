# Created automatically by Cursor AI (2024-12-19)

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from ..config import get_settings

logger = logging.getLogger(__name__)


class PlanType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UsageType(str, Enum):
    SEARCH_QUERIES = "search_queries"
    IMAGE_UPLOADS = "image_uploads"
    STORAGE_GB = "storage_gb"
    API_CALLS = "api_calls"
    EMBEDDING_GENERATION = "embedding_generation"
    INDEX_REBUILDS = "index_rebuilds"


class BillingStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


@dataclass
class PlanLimits:
    search_queries_per_month: int
    image_uploads_per_month: int
    storage_gb: int
    api_calls_per_month: int
    embedding_generation_per_month: int
    index_rebuilds_per_month: int
    max_collections: int
    max_users: int
    support_level: str


@dataclass
class PlanPricing:
    monthly_price: Decimal
    yearly_price: Decimal
    overage_rates: Dict[str, Decimal]


@dataclass
class TenantPlan:
    tenant_id: str
    plan_type: PlanType
    status: BillingStatus
    current_period_start: datetime
    current_period_end: datetime
    limits: PlanLimits
    pricing: PlanPricing
    auto_renew: bool = True
    trial_end: Optional[datetime] = None


@dataclass
class UsageRecord:
    tenant_id: str
    usage_type: UsageType
    quantity: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BillingPeriod:
    tenant_id: str
    period_start: datetime
    period_end: datetime
    usage: Dict[str, int]
    charges: Dict[str, Decimal]
    total_amount: Decimal
    status: str


class BillingService:
    def __init__(self):
        self.settings = get_settings()
        self.dynamodb = boto3.resource('dynamodb', region_name=self.settings.aws_region)
        self.sns = boto3.client('sns', region_name=self.settings.aws_region)
        
        # Initialize tables
        self.tenants_table = self.dynamodb.Table(f"{self.settings.environment}-tenants")
        self.usage_table = self.dynamodb.Table(f"{self.settings.environment}-usage")
        self.billing_table = self.dynamodb.Table(f"{self.settings.environment}-billing")
        
        # Define plan configurations
        self.plans = self._initialize_plans()
    
    def _initialize_plans(self) -> Dict[PlanType, Dict[str, Any]]:
        """Initialize plan configurations."""
        return {
            PlanType.FREE: {
                "limits": PlanLimits(
                    search_queries_per_month=1000,
                    image_uploads_per_month=100,
                    storage_gb=1,
                    api_calls_per_month=1000,
                    embedding_generation_per_month=1000,
                    index_rebuilds_per_month=1,
                    max_collections=1,
                    max_users=1,
                    support_level="community"
                ),
                "pricing": PlanPricing(
                    monthly_price=Decimal('0'),
                    yearly_price=Decimal('0'),
                    overage_rates={
                        "search_queries": Decimal('0.001'),
                        "image_uploads": Decimal('0.01'),
                        "storage_gb": Decimal('0.10'),
                        "api_calls": Decimal('0.0001'),
                        "embedding_generation": Decimal('0.001'),
                        "index_rebuilds": Decimal('1.00')
                    }
                )
            },
            PlanType.BASIC: {
                "limits": PlanLimits(
                    search_queries_per_month=10000,
                    image_uploads_per_month=1000,
                    storage_gb=10,
                    api_calls_per_month=10000,
                    embedding_generation_per_month=10000,
                    index_rebuilds_per_month=5,
                    max_collections=5,
                    max_users=5,
                    support_level="email"
                ),
                "pricing": PlanPricing(
                    monthly_price=Decimal('99'),
                    yearly_price=Decimal('990'),
                    overage_rates={
                        "search_queries": Decimal('0.0005'),
                        "image_uploads": Decimal('0.005'),
                        "storage_gb": Decimal('0.05'),
                        "api_calls": Decimal('0.00005'),
                        "embedding_generation": Decimal('0.0005'),
                        "index_rebuilds": Decimal('0.50')
                    }
                )
            },
            PlanType.PRO: {
                "limits": PlanLimits(
                    search_queries_per_month=100000,
                    image_uploads_per_month=10000,
                    storage_gb=100,
                    api_calls_per_month=100000,
                    embedding_generation_per_month=100000,
                    index_rebuilds_per_month=20,
                    max_collections=20,
                    max_users=20,
                    support_level="priority"
                ),
                "pricing": PlanPricing(
                    monthly_price=Decimal('299'),
                    yearly_price=Decimal('2990'),
                    overage_rates={
                        "search_queries": Decimal('0.0002'),
                        "image_uploads": Decimal('0.002'),
                        "storage_gb": Decimal('0.02'),
                        "api_calls": Decimal('0.00002'),
                        "embedding_generation": Decimal('0.0002'),
                        "index_rebuilds": Decimal('0.20')
                    }
                )
            },
            PlanType.ENTERPRISE: {
                "limits": PlanLimits(
                    search_queries_per_month=1000000,
                    image_uploads_per_month=100000,
                    storage_gb=1000,
                    api_calls_per_month=1000000,
                    embedding_generation_per_month=1000000,
                    index_rebuilds_per_month=100,
                    max_collections=100,
                    max_users=100,
                    support_level="dedicated"
                ),
                "pricing": PlanPricing(
                    monthly_price=Decimal('999'),
                    yearly_price=Decimal('9990'),
                    overage_rates={
                        "search_queries": Decimal('0.0001'),
                        "image_uploads": Decimal('0.001'),
                        "storage_gb": Decimal('0.01'),
                        "api_calls": Decimal('0.00001'),
                        "embedding_generation": Decimal('0.0001'),
                        "index_rebuilds": Decimal('0.10')
                    }
                )
            }
        }
    
    async def create_tenant(self, tenant_id: str, plan_type: PlanType = PlanType.FREE) -> TenantPlan:
        """Create a new tenant with the specified plan."""
        try:
            plan_config = self.plans[plan_type]
            current_time = datetime.utcnow()
            
            # Set trial period for paid plans
            trial_end = None
            if plan_type != PlanType.FREE:
                trial_end = current_time + timedelta(days=14)
            
            tenant_plan = TenantPlan(
                tenant_id=tenant_id,
                plan_type=plan_type,
                status=BillingStatus.ACTIVE,
                current_period_start=current_time,
                current_period_end=current_time + timedelta(days=30),
                limits=plan_config["limits"],
                pricing=plan_config["pricing"],
                trial_end=trial_end
            )
            
            # Store in DynamoDB
            await self._store_tenant_plan(tenant_plan)
            
            logger.info(f"Created tenant {tenant_id} with plan {plan_type}")
            return tenant_plan
            
        except Exception as e:
            logger.error(f"Failed to create tenant {tenant_id}: {e}")
            raise
    
    async def get_tenant_plan(self, tenant_id: str) -> Optional[TenantPlan]:
        """Get tenant plan information."""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.tenants_table.get_item, {"tenant_id": tenant_id}
            )
            
            if "Item" not in response:
                return None
            
            item = response["Item"]
            return self._deserialize_tenant_plan(item)
            
        except Exception as e:
            logger.error(f"Failed to get tenant plan for {tenant_id}: {e}")
            return None
    
    async def update_tenant_plan(self, tenant_id: str, plan_type: PlanType) -> TenantPlan:
        """Update tenant plan."""
        try:
            plan_config = self.plans[plan_type]
            current_time = datetime.utcnow()
            
            tenant_plan = TenantPlan(
                tenant_id=tenant_id,
                plan_type=plan_type,
                status=BillingStatus.ACTIVE,
                current_period_start=current_time,
                current_period_end=current_time + timedelta(days=30),
                limits=plan_config["limits"],
                pricing=plan_config["pricing"]
            )
            
            await self._store_tenant_plan(tenant_plan)
            
            logger.info(f"Updated tenant {tenant_id} to plan {plan_type}")
            return tenant_plan
            
        except Exception as e:
            logger.error(f"Failed to update tenant plan for {tenant_id}: {e}")
            raise
    
    async def record_usage(self, tenant_id: str, usage_type: UsageType, quantity: int = 1, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record usage for a tenant."""
        try:
            usage_record = UsageRecord(
                tenant_id=tenant_id,
                usage_type=usage_type,
                quantity=quantity,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            # Store usage record
            await asyncio.get_event_loop().run_in_executor(
                None, self.usage_table.put_item,
                {
                    "tenant_id": usage_record.tenant_id,
                    "usage_type": usage_record.usage_type.value,
                    "timestamp": usage_record.timestamp.isoformat(),
                    "quantity": usage_record.quantity,
                    "metadata": json.dumps(usage_record.metadata) if usage_record.metadata else None
                }
            )
            
            # Check if usage exceeds limits
            await self._check_usage_limits(tenant_id, usage_type, quantity)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record usage for tenant {tenant_id}: {e}")
            return False
    
    async def get_usage_summary(self, tenant_id: str, period_start: datetime, period_end: datetime) -> Dict[str, int]:
        """Get usage summary for a tenant in a given period."""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.usage_table.query,
                {
                    "KeyConditionExpression": "tenant_id = :tenant_id AND #ts BETWEEN :start AND :end",
                    "ExpressionAttributeNames": {"#ts": "timestamp"},
                    "ExpressionAttributeValues": {
                        ":tenant_id": tenant_id,
                        ":start": period_start.isoformat(),
                        ":end": period_end.isoformat()
                    }
                }
            )
            
            usage_summary = {}
            for item in response.get("Items", []):
                usage_type = item["usage_type"]
                quantity = item["quantity"]
                usage_summary[usage_type] = usage_summary.get(usage_type, 0) + quantity
            
            return usage_summary
            
        except Exception as e:
            logger.error(f"Failed to get usage summary for tenant {tenant_id}: {e}")
            return {}
    
    async def calculate_billing(self, tenant_id: str, period_start: datetime, period_end: datetime) -> BillingPeriod:
        """Calculate billing for a tenant in a given period."""
        try:
            tenant_plan = await self.get_tenant_plan(tenant_id)
            if not tenant_plan:
                raise ValueError(f"Tenant {tenant_id} not found")
            
            usage_summary = await self.get_usage_summary(tenant_id, period_start, period_end)
            
            # Calculate charges
            charges = {}
            total_amount = Decimal('0')
            
            # Base plan charge
            if tenant_plan.plan_type != PlanType.FREE:
                total_amount += tenant_plan.pricing.monthly_price
            
            # Overage charges
            for usage_type, quantity in usage_summary.items():
                limit_key = f"{usage_type}_per_month"
                limit_value = getattr(tenant_plan.limits, limit_key, 0)
                
                if quantity > limit_value:
                    overage = quantity - limit_value
                    overage_rate = tenant_plan.pricing.overage_rates.get(usage_type, Decimal('0'))
                    overage_charge = overage_rate * overage
                    charges[f"{usage_type}_overage"] = overage_charge
                    total_amount += overage_charge
            
            billing_period = BillingPeriod(
                tenant_id=tenant_id,
                period_start=period_start,
                period_end=period_end,
                usage=usage_summary,
                charges=charges,
                total_amount=total_amount,
                status="calculated"
            )
            
            # Store billing period
            await self._store_billing_period(billing_period)
            
            return billing_period
            
        except Exception as e:
            logger.error(f"Failed to calculate billing for tenant {tenant_id}: {e}")
            raise
    
    async def check_usage_limits(self, tenant_id: str, usage_type: UsageType, quantity: int = 1) -> bool:
        """Check if usage would exceed limits."""
        try:
            tenant_plan = await self.get_tenant_plan(tenant_id)
            if not tenant_plan:
                return False
            
            # Get current usage for the month
            current_time = datetime.utcnow()
            month_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_usage = await self.get_usage_summary(tenant_id, month_start, current_time)
            
            # Check limits
            limit_key = f"{usage_type.value}_per_month"
            limit_value = getattr(tenant_plan.limits, limit_key, 0)
            current_quantity = current_usage.get(usage_type.value, 0)
            
            return (current_quantity + quantity) <= limit_value
            
        except Exception as e:
            logger.error(f"Failed to check usage limits for tenant {tenant_id}: {e}")
            return False
    
    async def _check_usage_limits(self, tenant_id: str, usage_type: UsageType, quantity: int):
        """Internal method to check usage limits and send notifications."""
        try:
            tenant_plan = await self.get_tenant_plan(tenant_id)
            if not tenant_plan:
                return
            
            # Get current usage
            current_time = datetime.utcnow()
            month_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_usage = await self.get_usage_summary(tenant_id, month_start, current_time)
            
            limit_key = f"{usage_type.value}_per_month"
            limit_value = getattr(tenant_plan.limits, limit_key, 0)
            current_quantity = current_usage.get(usage_type.value, 0)
            
            # Check if approaching limit (80% threshold)
            if current_quantity >= limit_value * 0.8:
                await self._send_usage_alert(tenant_id, usage_type, current_quantity, limit_value, "approaching")
            
            # Check if exceeded limit
            if current_quantity >= limit_value:
                await self._send_usage_alert(tenant_id, usage_type, current_quantity, limit_value, "exceeded")
                
        except Exception as e:
            logger.error(f"Failed to check usage limits: {e}")
    
    async def _send_usage_alert(self, tenant_id: str, usage_type: UsageType, current: int, limit: int, status: str):
        """Send usage alert notification."""
        try:
            message = {
                "tenant_id": tenant_id,
                "usage_type": usage_type.value,
                "current_usage": current,
                "limit": limit,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send SNS notification
            await asyncio.get_event_loop().run_in_executor(
                None, self.sns.publish,
                TopicArn=self.settings.billing_sns_topic_arn,
                Message=json.dumps(message)
            )
            
            logger.info(f"Sent usage alert for tenant {tenant_id}: {status}")
            
        except Exception as e:
            logger.error(f"Failed to send usage alert: {e}")
    
    async def _store_tenant_plan(self, tenant_plan: TenantPlan):
        """Store tenant plan in DynamoDB."""
        item = {
            "tenant_id": tenant_plan.tenant_id,
            "plan_type": tenant_plan.plan_type.value,
            "status": tenant_plan.status.value,
            "current_period_start": tenant_plan.current_period_start.isoformat(),
            "current_period_end": tenant_plan.current_period_end.isoformat(),
            "limits": {
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
            "pricing": {
                "monthly_price": str(tenant_plan.pricing.monthly_price),
                "yearly_price": str(tenant_plan.pricing.yearly_price),
                "overage_rates": {k: str(v) for k, v in tenant_plan.pricing.overage_rates.items()}
            },
            "auto_renew": tenant_plan.auto_renew
        }
        
        if tenant_plan.trial_end:
            item["trial_end"] = tenant_plan.trial_end.isoformat()
        
        await asyncio.get_event_loop().run_in_executor(
            None, self.tenants_table.put_item, item
        )
    
    async def _store_billing_period(self, billing_period: BillingPeriod):
        """Store billing period in DynamoDB."""
        item = {
            "tenant_id": billing_period.tenant_id,
            "period_start": billing_period.period_start.isoformat(),
            "period_end": billing_period.period_end.isoformat(),
            "usage": billing_period.usage,
            "charges": {k: str(v) for k, v in billing_period.charges.items()},
            "total_amount": str(billing_period.total_amount),
            "status": billing_period.status
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None, self.billing_table.put_item, item
        )
    
    def _deserialize_tenant_plan(self, item: Dict[str, Any]) -> TenantPlan:
        """Deserialize tenant plan from DynamoDB item."""
        limits_data = item["limits"]
        pricing_data = item["pricing"]
        
        limits = PlanLimits(
            search_queries_per_month=limits_data["search_queries_per_month"],
            image_uploads_per_month=limits_data["image_uploads_per_month"],
            storage_gb=limits_data["storage_gb"],
            api_calls_per_month=limits_data["api_calls_per_month"],
            embedding_generation_per_month=limits_data["embedding_generation_per_month"],
            index_rebuilds_per_month=limits_data["index_rebuilds_per_month"],
            max_collections=limits_data["max_collections"],
            max_users=limits_data["max_users"],
            support_level=limits_data["support_level"]
        )
        
        pricing = PlanPricing(
            monthly_price=Decimal(pricing_data["monthly_price"]),
            yearly_price=Decimal(pricing_data["yearly_price"]),
            overage_rates={k: Decimal(v) for k, v in pricing_data["overage_rates"].items()}
        )
        
        return TenantPlan(
            tenant_id=item["tenant_id"],
            plan_type=PlanType(item["plan_type"]),
            status=BillingStatus(item["status"]),
            current_period_start=datetime.fromisoformat(item["current_period_start"]),
            current_period_end=datetime.fromisoformat(item["current_period_end"]),
            limits=limits,
            pricing=pricing,
            auto_renew=item.get("auto_renew", True),
            trial_end=datetime.fromisoformat(item["trial_end"]) if "trial_end" in item else None
        )
