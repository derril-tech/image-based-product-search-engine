import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ReportsController } from './reports.controller';
import { ReportsService } from './reports.service';
import { SearchSession } from '../entities/search-session.entity';
import { SearchFeedback } from '../entities/search-feedback.entity';
import { Organization } from '../entities/organization.entity';

@Module({
    imports: [
        TypeOrmModule.forFeature([SearchSession, SearchFeedback, Organization]),
    ],
    controllers: [ReportsController],
    providers: [ReportsService],
    exports: [ReportsService],
})
export class ReportsModule { }
