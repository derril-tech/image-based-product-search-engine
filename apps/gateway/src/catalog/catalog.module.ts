import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CatalogController } from './catalog.controller';
import { CatalogService } from './catalog.service';
import { Product } from '../entities/product.entity';
import { ProductVariant } from '../entities/product-variant.entity';
import { Image } from '../entities/image.entity';
import { Organization } from '../entities/organization.entity';

@Module({
    imports: [
        TypeOrmModule.forFeature([Product, ProductVariant, Image, Organization]),
    ],
    controllers: [CatalogController],
    providers: [CatalogService],
    exports: [CatalogService],
})
export class CatalogModule { }
