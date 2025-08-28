import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    ManyToOne,
    OneToMany,
    Index,
} from 'typeorm';
import { Organization } from './organization.entity';
import { ProductVariant } from './product-variant.entity';
import { Image } from './image.entity';

@Entity('products')
@Index(['organizationId'])
@Index(['externalId'])
@Index(['category'])
@Index(['brand'])
export class Product {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column({ type: 'uuid' })
    organizationId: string;

    @Column({ type: 'varchar', length: 255, nullable: true })
    externalId: string;

    @Column({ type: 'varchar', length: 500 })
    name: string;

    @Column({ type: 'text', nullable: true })
    description: string;

    @Column({ type: 'varchar', length: 255, nullable: true })
    brand: string;

    @Column({ type: 'varchar', length: 255, nullable: true })
    category: string;

    @Column({ type: 'text', array: true, default: [] })
    tags: string[];

    @Column({ type: 'jsonb', default: {} })
    metadata: Record<string, any>;

    @Column({ type: 'boolean', default: true })
    isActive: boolean;

    @CreateDateColumn({ type: 'timestamp with time zone' })
    createdAt: Date;

    @UpdateDateColumn({ type: 'timestamp with time zone' })
    updatedAt: Date;

    // Relations
    @ManyToOne(() => Organization, (organization) => organization.products)
    organization: Organization;

    @OneToMany(() => ProductVariant, (variant) => variant.product)
    variants: ProductVariant[];

    @OneToMany(() => Image, (image) => image.product)
    images: Image[];
}
