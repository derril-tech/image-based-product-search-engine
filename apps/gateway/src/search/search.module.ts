import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { SearchController } from './search.controller';
import { SearchService } from './search.service';
import { SearchSession } from '../entities/search-session.entity';
import { SearchFeedback } from '../entities/search-feedback.entity';
import { Organization } from '../entities/organization.entity';

@Module({
    imports: [
        TypeOrmModule.forFeature([SearchSession, SearchFeedback, Organization]),
    ],
    controllers: [SearchController],
    providers: [SearchService],
    exports: [SearchService],
})
export class SearchModule { }
