---
name: add-frontend-feature
description: Add a new frontend feature module (model, service, components, routes)
---

# Add Frontend Feature

Follow these steps exactly when adding a new frontend feature:

## Steps

1. **Model** — Create `frontend/src/app/features/{feature}/models/{feature}.model.ts`
   - Interface for full entity, Create input, and constants
   - Field names must match backend Response schema exactly

2. **Service** — Create `frontend/src/app/features/{feature}/services/{feature}.service.ts`
   - `@Injectable({ providedIn: 'root' })`
   - Inject `ApiService` with `inject()`
   - Methods: `getAll()`, `getById(id)`, `create(data)`, `update(id, data)`, `delete(id)`
   - Return `Observable<T>`

3. **List component** — Create `features/{feature}/{feature}-list/`
   - `.component.ts`, `.component.html`, `.component.scss`
   - `standalone: true` with `imports: [...]`
   - Use `inject()` for dependencies
   - Load data in `ngOnInit`

4. **Form component** — Create `features/{feature}/{feature}-form/`
   - Reusable for create and edit modes
   - Use Angular Material form fields
   - Reactive forms or template-driven

5. **Routes** — Create `features/{feature}/{feature}.routes.ts`
   ```typescript
   export const FEATURE_ROUTES: Routes = [
     { path: '', component: FeatureListComponent },
     { path: 'new', component: FeatureFormComponent },
     { path: ':id', component: FeatureDetailComponent },
     { path: ':id/edit', component: FeatureFormComponent },
   ];
   ```

6. **Register routes** — Add to `app.routes.ts` under LayoutComponent children:
   ```typescript
   { path: '{feature}', loadChildren: () => import('./features/{feature}/{feature}.routes').then(m => m.FEATURE_ROUTES) }
   ```

7. **Sidebar link** — Add navigation item in `layout/sidebar/sidebar.component.html`

8. **Styling** — Use CSS variables only (`var(--name)`). Never hardcode hex colors.

9. **Rebuild**:
   ```bash
   docker-compose build --no-cache frontend && docker-compose up -d
   ```
