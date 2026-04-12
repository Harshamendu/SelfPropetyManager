import { Routes } from '@angular/router';

export const DOCUMENT_GEN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./template-list/template-list.component').then(m => m.TemplateListComponent)
  },
  {
    path: 'new',
    loadComponent: () =>
      import('./template-form/template-form.component').then(m => m.TemplateFormComponent)
  },
  {
    path: ':id/edit',
    loadComponent: () =>
      import('./template-form/template-form.component').then(m => m.TemplateFormComponent)
  }
];
