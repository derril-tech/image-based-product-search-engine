import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY, Role } from '../decorators/roles.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
    constructor(private reflector: Reflector) { }

    canActivate(context: ExecutionContext): boolean {
        const requiredRoles = this.reflector.getAllAndOverride<Role[]>(ROLES_KEY, [
            context.getHandler(),
            context.getClass(),
        ]);

        if (!requiredRoles) {
            return true;
        }

        const { user } = context.switchToHttp().getRequest();

        if (!user) {
            return false;
        }

        // Check if user has any of the required roles
        return requiredRoles.some((role) => {
            switch (role) {
                case Role.USER:
                    return true; // All authenticated users have USER role
                case Role.ADMIN:
                    return user.role === 'admin' || user.membershipRole === 'admin' || user.membershipRole === 'owner';
                case Role.OWNER:
                    return user.membershipRole === 'owner';
                default:
                    return false;
            }
        });
    }
}
