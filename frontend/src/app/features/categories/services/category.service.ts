import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { Category, CategoryCreate } from '../models/category.model';

@Injectable({ providedIn: 'root' })
export class CategoryService {
  private api = inject(ApiService);

  getAll(categoryType?: string, propertyId?: string): Observable<Category[]> {
    const params: Record<string, string> = {};
    if (categoryType) params['category_type'] = categoryType;
    if (propertyId) params['property_id'] = propertyId;
    return this.api.get<Category[]>('/categories', params);
  }

  create(data: CategoryCreate): Observable<Category> {
    return this.api.post<Category>('/categories', data);
  }

  update(id: string, data: Partial<CategoryCreate>): Observable<Category> {
    return this.api.put<Category>(`/categories/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/categories/${id}`);
  }
}
