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
import { SearchSession } from './search-session.entity';

export enum UserRole {
    ADMIN = 'admin',
    USER = 'user',
}

@Entity('users')
@Index(['email'], { unique: true })
export class User {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column({ type: 'varchar', length: 255, unique: true })
    email: string;

    @Column({ type: 'varchar', length: 255 })
    passwordHash: string;

    @Column({ type: 'varchar', length: 100, nullable: true })
    firstName: string;

    @Column({ type: 'varchar', length: 100, nullable: true })
    lastName: string;

    @Column({
        type: 'enum',
        enum: UserRole,
        default: UserRole.USER,
    })
    role: UserRole;

    @Column({ type: 'boolean', default: true })
    isActive: boolean;

    @Column({ type: 'boolean', default: false })
    emailVerified: boolean;

    @Column({ type: 'timestamp with time zone', nullable: true })
    lastLogin: Date;

    @CreateDateColumn({ type: 'timestamp with time zone' })
    createdAt: Date;

    @UpdateDateColumn({ type: 'timestamp with time zone' })
    updatedAt: Date;

    // Relations
    @OneToMany(
        () => OrganizationMembership,
        (membership) => membership.user,
    )
    memberships: OrganizationMembership[];

    @OneToMany(() => SearchSession, (session) => session.user)
    searchSessions: SearchSession[];
}
