import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, Router } from '@angular/router';
import { AuthService, UserRole } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated) {
    return router.createUrlTree(['/login']);
  }

  const allowed = (route.data?.['roles'] as UserRole[] | undefined) ?? [];
  if (allowed.length === 0 || authService.hasRole(...allowed)) {
    return true;
  }

  return router.createUrlTree([authService.isTenant() ? '/my-rental' : '/dashboard']);
};
