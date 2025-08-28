import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    OneToMany,
    Index,
} from 'typeorm';
import { OrganizationMembership } from './organization-membership.entity';
import { Product } from './product.entity';
import { Image } from './image.entity';
import { Connector } from './connector.entity';

export enum OrganizationPlan {
    FREE = 'free',
    PRO = 'pro',
    ENTERPRISE = 'enterprise',
}

@Entity('organizations')
@Index(['slug'], { unique: true })
export class Organization {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column({ type: 'varchar', length: 255 })
    name: string;

    @Column({ type: 'varchar', length: 100, unique: true })
    slug: string;

    @Column({
        type: 'enum',
        enum: OrganizationPlan,
        default: OrganizationPlan.FREE,
    })
    plan: OrganizationPlan;

    @Column({ type: 'jsonb', default: {} })
    settings: Record<string, any>;

    @CreateDateColumn({ type: 'timestamp with time zone' })
    createdAt: Date;

    @UpdateDateColumn({ type: 'timestamp with time zone' })
    updatedAt: Date;

    // Relations
    @OneToMany(
        () => OrganizationMembership,
        (membership) => membership.organization,
    )
    memberships: OrganizationMembership[];

    @OneToMany(() => Product, (product) => product.organization)
    products: Product[];

    @OneToMany(() => Image, (image) => image.organization)
    images: Image[];

    @OneToMany(() => Connector, (connector) => connector.organization)
    connectors: Connector[];
}
