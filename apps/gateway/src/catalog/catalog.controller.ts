import {
    Controller,
    Get,
    Post,
    Put,
    Delete,
    Body,
    Param,
    Query,
    UseGuards,
    Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { CatalogService } from './catalog.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { CreateProductDto } from './dto/create-product.dto';
import { UpdateProductDto } from './dto/update-product.dto';
import { CreateImageDto } from './dto/create-image.dto';

@ApiTags('Catalog')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('catalog')
export class CatalogController {
    constructor(private readonly catalogService: CatalogService) { }

    @Get('products')
    @ApiOperation({ summary: 'Get all products for organization' })
    @ApiResponse({ status: 200, description: 'Products retrieved successfully' })
    async getProducts(@Request() req, @Query() query: any) {
        return this.catalogService.getProducts(req.user.organizationId, query);
    }

    @Get('products/:id')
    @ApiOperation({ summary: 'Get product by ID' })
    @ApiResponse({ status: 200, description: 'Product retrieved successfully' })
    @ApiResponse({ status: 404, description: 'Product not found' })
    async getProduct(@Param('id') id: string, @Request() req) {
        return this.catalogService.getProduct(id, req.user.organizationId);
    }

    @Post('products')
    @ApiOperation({ summary: 'Create a new product' })
    @ApiResponse({ status: 201, description: 'Product created successfully' })
    async createProduct(@Body() createProductDto: CreateProductDto, @Request() req) {
        return this.catalogService.createProduct(createProductDto, req.user.organizationId);
    }

    @Put('products/:id')
    @ApiOperation({ summary: 'Update a product' })
    @ApiResponse({ status: 200, description: 'Product updated successfully' })
    async updateProduct(
        @Param('id') id: string,
        @Body() updateProductDto: UpdateProductDto,
        @Request() req,
    ) {
        return this.catalogService.updateProduct(id, updateProductDto, req.user.organizationId);
    }

    @Delete('products/:id')
    @ApiOperation({ summary: 'Delete a product' })
    @ApiResponse({ status: 200, description: 'Product deleted successfully' })
    async deleteProduct(@Param('id') id: string, @Request() req) {
        return this.catalogService.deleteProduct(id, req.user.organizationId);
    }

    @Post('products/:id/images')
    @ApiOperation({ summary: 'Add image to product' })
    @ApiResponse({ status: 201, description: 'Image added successfully' })
    async addImage(
        @Param('id') productId: string,
        @Body() createImageDto: CreateImageDto,
        @Request() req,
    ) {
        return this.catalogService.addImage(productId, createImageDto, req.user.organizationId);
    }

    @Get('images')
    @ApiOperation({ summary: 'Get all images for organization' })
    @ApiResponse({ status: 200, description: 'Images retrieved successfully' })
    async getImages(@Request() req, @Query() query: any) {
        return this.catalogService.getImages(req.user.organizationId, query);
    }
}
