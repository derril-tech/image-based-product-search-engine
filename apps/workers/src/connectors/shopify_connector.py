"""Shopify connector for data ingestion."""

import aiohttp
import logging
from typing import Dict, Any, List
from ..models.ingest_models import ConnectorInfo, ConnectionTestResult, ConnectorType

logger = logging.getLogger(__name__)

class ShopifyConnector:
    """Connector for Shopify stores."""
    
    def __init__(self):
        self.base_url = None
        self.access_token = None
        self.api_version = "2023-10"
    
    async def get_info(self) -> ConnectorInfo:
        """Get connector information."""
        return ConnectorInfo(
            id="shopify",
            name="Shopify",
            type=ConnectorType.SHOPIFY,
            description="Import products and images from Shopify stores",
            config_schema={
                "type": "object",
                "properties": {
                    "shop_domain": {
                        "type": "string",
                        "description": "Shopify store domain (e.g., mystore.myshopify.com)"
                    },
                    "access_token": {
                        "type": "string",
                        "description": "Shopify API access token"
                    },
                    "api_version": {
                        "type": "string",
                        "description": "Shopify API version",
                        "default": "2023-10"
                    }
                },
                "required": ["shop_domain", "access_token"]
            },
            supported_features=["products", "images", "variants", "collections"]
        )
    
    async def test_connection(self, config: Dict[str, Any] = None) -> ConnectionTestResult:
        """Test connection to Shopify store."""
        try:
            if config:
                self.base_url = f"https://{config['shop_domain']}/admin/api/{config.get('api_version', self.api_version)}"
                self.access_token = config['access_token']
            
            if not self.base_url or not self.access_token:
                return ConnectionTestResult(
                    success=False,
                    message="Missing configuration: shop_domain and access_token required"
                )
            
            headers = {
                "X-Shopify-Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/shop.json", headers=headers) as response:
                    if response.status == 200:
                        shop_data = await response.json()
                        return ConnectionTestResult(
                            success=True,
                            message=f"Successfully connected to {shop_data['shop']['name']}",
                            details={"shop_name": shop_data['shop']['name']}
                        )
                    else:
                        return ConnectionTestResult(
                            success=False,
                            message=f"Connection failed: {response.status} {response.reason}"
                        )
                        
        except Exception as e:
            logger.error(f"Shopify connection test failed: {str(e)}")
            return ConnectionTestResult(
                success=False,
                message=f"Connection test failed: {str(e)}"
            )
    
    async def fetch_data(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data from Shopify store."""
        if config:
            self.base_url = f"https://{config['shop_domain']}/admin/api/{config.get('api_version', self.api_version)}"
            self.access_token = config['access_token']
        
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        data = {
            "products": [],
            "images": [],
            "variants": []
        }
        
        async with aiohttp.ClientSession() as session:
            # Fetch products
            products_url = f"{self.base_url}/products.json"
            async with session.get(products_url, headers=headers) as response:
                if response.status == 200:
                    products_data = await response.json()
                    data["products"] = products_data.get("products", [])
                    
                    # Fetch images for each product
                    for product in data["products"]:
                        images_url = f"{self.base_url}/products/{product['id']}/images.json"
                        async with session.get(images_url, headers=headers) as img_response:
                            if img_response.status == 200:
                                images_data = await img_response.json()
                                for image in images_data.get("images", []):
                                    image["product_id"] = product["id"]
                                    data["images"].append(image)
                
                # Fetch variants
                variants_url = f"{self.base_url}/variants.json"
                async with session.get(variants_url, headers=headers) as response:
                    if response.status == 200:
                        variants_data = await response.json()
                        data["variants"] = variants_data.get("variants", [])
        
        return data
    
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize Shopify data."""
        processed_data = {
            "products": [],
            "images": [],
            "variants": []
        }
        
        # Process products
        for product in raw_data.get("products", []):
            processed_product = {
                "external_id": str(product["id"]),
                "name": product["title"],
                "description": product.get("body_html", ""),
                "brand": product.get("vendor", ""),
                "category": product.get("product_type", ""),
                "tags": product.get("tags", "").split(",") if product.get("tags") else [],
                "metadata": {
                    "shopify_id": product["id"],
                    "handle": product.get("handle", ""),
                    "status": product.get("status", ""),
                    "created_at": product.get("created_at", ""),
                    "updated_at": product.get("updated_at", "")
                }
            }
            processed_data["products"].append(processed_product)
        
        # Process images
        for image in raw_data.get("images", []):
            processed_image = {
                "url": image.get("src", ""),
                "filename": f"shopify_{image['product_id']}_{image['id']}.jpg",
                "mime_type": "image/jpeg",
                "size": 0,  # Will be updated during download
                "width": image.get("width", 0),
                "height": image.get("height", 0),
                "alt_text": image.get("alt", ""),
                "is_primary": image.get("position", 0) == 1,
                "metadata": {
                    "shopify_id": image["id"],
                    "product_id": image["product_id"],
                    "position": image.get("position", 0)
                }
            }
            processed_data["images"].append(processed_image)
        
        # Process variants
        for variant in raw_data.get("variants", []):
            processed_variant = {
                "external_id": str(variant["id"]),
                "sku": variant.get("sku", ""),
                "name": variant.get("title", ""),
                "price": float(variant.get("price", 0)),
                "currency": "USD",  # Default for Shopify
                "attributes": {
                    "weight": variant.get("weight", 0),
                    "weight_unit": variant.get("weight_unit", ""),
                    "inventory_quantity": variant.get("inventory_quantity", 0),
                    "option1": variant.get("option1", ""),
                    "option2": variant.get("option2", ""),
                    "option3": variant.get("option3", "")
                },
                "metadata": {
                    "shopify_id": variant["id"],
                    "product_id": variant["product_id"]
                }
            }
            processed_data["variants"].append(processed_variant)
        
        return processed_data
    
    async def save_data(self, processed_data: Dict[str, Any]):
        """Save processed data to database."""
        # This would typically save to the database
        # For now, just log the data
        logger.info(f"Would save {len(processed_data['products'])} products")
        logger.info(f"Would save {len(processed_data['images'])} images")
        logger.info(f"Would save {len(processed_data['variants'])} variants")
        
        # In a real implementation, this would:
        # 1. Save products to the products table
        # 2. Save images to the images table
        # 3. Save variants to the product_variants table
        # 4. Handle relationships between entities
        # 5. Queue images for processing (resize, embedding, etc.)
