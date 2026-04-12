import { Routes } from '@angular/router';

export const REPORTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./year-end-export/year-end-export.component').then(m => m.YearEndExportComponent)
  }
];
