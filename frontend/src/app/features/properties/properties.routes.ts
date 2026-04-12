import { Routes } from '@angular/router';

export const PROPERTIES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./property-list/property-list.component').then(m => m.PropertyListComponent)
  },
  {
    path: 'new',
    loadComponent: () =>
      import('./property-form/property-form.component').then(m => m.PropertyFormComponent)
  },
  {
    path: ':id',
    loadComponent: () =>
      import('./property-detail/property-detail.component').then(m => m.PropertyDetailComponent)
  },
  {
    path: ':id/edit',
    loadComponent: () =>
      import('./property-form/property-form.component').then(m => m.PropertyFormComponent)
  }
];
