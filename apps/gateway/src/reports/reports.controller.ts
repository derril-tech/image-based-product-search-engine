import {
    Controller,
    Get,
    Query,
    UseGuards,
    Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { ReportsService } from './reports.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@ApiTags('Reports')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('reports')
export class ReportsController {
    constructor(private readonly reportsService: ReportsService) { }

    @Get('search-metrics')
    @ApiOperation({ summary: 'Get search metrics' })
    @ApiResponse({ status: 200, description: 'Search metrics retrieved' })
    async getSearchMetrics(@Request() req, @Query() query: any) {
        return this.reportsService.getSearchMetrics(req.user.organizationId, query);
    }

    @Get('search-quality')
    @ApiOperation({ summary: 'Get search quality metrics' })
    @ApiResponse({ status: 200, description: 'Search quality metrics retrieved' })
    async getSearchQualityMetrics(@Request() req, @Query() query: any) {
        return this.reportsService.getSearchQualityMetrics(req.user.organizationId, query);
    }

    @Get('popular-searches')
    @ApiOperation({ summary: 'Get popular searches' })
    @ApiResponse({ status: 200, description: 'Popular searches retrieved' })
    async getPopularSearches(@Request() req, @Query() query: any) {
        return this.reportsService.getPopularSearches(req.user.organizationId, query);
    }

    @Get('user-activity')
    @ApiOperation({ summary: 'Get user activity metrics' })
    @ApiResponse({ status: 200, description: 'User activity metrics retrieved' })
    async getUserActivityMetrics(@Request() req, @Query() query: any) {
        return this.reportsService.getUserActivityMetrics(req.user.organizationId, query);
    }
}
