import {
    Injectable,
    NestInterceptor,
    ExecutionContext,
    CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { DataSource } from 'typeorm';

@Injectable()
export class RlsInterceptor implements NestInterceptor {
    constructor(private dataSource: DataSource) { }

    intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
        const request = context.switchToHttp().getRequest();
        const user = request.user;

        if (user) {
            // Set user context for RLS policies
            return next.handle().pipe(
                tap(() => {
                    this.dataSource.query(
                        'SELECT set_user_context($1, $2)',
                        [user.id, user.organizationId],
                    );
                }),
            );
        }

        return next.handle();
    }
}
