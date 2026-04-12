import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { LayoutComponent } from './layout/layout.component';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';
import { roleGuard } from './core/guards/role.guard';
import { AuthService } from './core/services/auth.service';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login.component').then(m => m.LoginComponent)
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: () => {
      const authService = inject(AuthService);
      if (!authService.isAuthenticated) return '/login';
      return authService.isTenant() ? '/my-rental' : '/dashboard';
    }
  },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        canActivate: [roleGuard],
        data: { roles: ['admin', 'property_manager'] },
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'my-rental',
        canActivate: [roleGuard],
        data: { roles: ['tenant'] },
        loadChildren: () =>
          import('./features/tenant/tenant.routes').then(m => m.TENANT_ROUTES)
      },
      {
        path: 'users',
        canActivate: [adminGuard],
        loadChildren: () =>
          import('./features/users/users.routes').then(m => m.USERS_ROUTES)
      },
      {
        path: 'properties',
        canActivate: [roleGuard],
        data: { roles: ['admin', 'property_manager'] },
        loadChildren: () =>
          import('./features/properties/properties.routes').then(m => m.PROPERTIES_ROUTES)
      },
      {
        path: 'reports',
        canActivate: [roleGuard],
        data: { roles: ['admin', 'property_manager'] },
        loadChildren: () =>
          import('./features/reports/reports.routes').then(m => m.REPORTS_ROUTES)
      },
      {
        path: 'document-templates',
        canActivate: [roleGuard],
        data: { roles: ['admin', 'property_manager'] },
        loadChildren: () =>
          import('./features/document-gen/document-gen.routes').then(m => m.DOCUMENT_GEN_ROUTES)
      },
      {
        path: 'backups',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./features/backups/backup-manager/backup-manager.component').then(m => m.BackupManagerComponent)
      }
    ]
  }
];
