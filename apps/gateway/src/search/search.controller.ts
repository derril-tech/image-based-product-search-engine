import {
    Controller,
    Post,
    Body,
    UseGuards,
    Request,
    Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { SearchService } from './search.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { SearchQueryDto } from './dto/search-query.dto';
import { SearchFeedbackDto } from './dto/search-feedback.dto';

@ApiTags('Search')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('search')
export class SearchController {
    constructor(private readonly searchService: SearchService) { }

    @Post('image')
    @ApiOperation({ summary: 'Search by image' })
    @ApiResponse({ status: 200, description: 'Search results' })
    async searchByImage(@Body() searchQueryDto: SearchQueryDto, @Request() req) {
        return this.searchService.searchByImage(searchQueryDto, req.user);
    }

    @Post('text')
    @ApiOperation({ summary: 'Search by text' })
    @ApiResponse({ status: 200, description: 'Search results' })
    async searchByText(@Body() searchQueryDto: SearchQueryDto, @Request() req) {
        return this.searchService.searchByText(searchQueryDto, req.user);
    }

    @Post('feedback')
    @ApiOperation({ summary: 'Submit search feedback' })
    @ApiResponse({ status: 201, description: 'Feedback submitted successfully' })
    async submitFeedback(@Body() feedbackDto: SearchFeedbackDto, @Request() req) {
        return this.searchService.submitFeedback(feedbackDto, req.user);
    }

    @Post('sessions')
    @ApiOperation({ summary: 'Get search sessions' })
    @ApiResponse({ status: 200, description: 'Search sessions retrieved' })
    async getSearchSessions(@Request() req, @Query() query: any) {
        return this.searchService.getSearchSessions(req.user, query);
    }
}
