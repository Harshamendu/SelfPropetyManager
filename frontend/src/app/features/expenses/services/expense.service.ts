import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { Expense, ExpenseCreate } from '../models/expense.model';

@Injectable({ providedIn: 'root' })
export class ExpenseService {
  private api = inject(ApiService);

  getByProperty(propertyId: string, year?: number, category?: string): Observable<Expense[]> {
    const params: Record<string, string | number> = {};
    if (year) params['year'] = year;
    if (category) params['category'] = category;
    return this.api.get<Expense[]>(`/properties/${propertyId}/expenses`, params);
  }

  create(propertyId: string, data: ExpenseCreate): Observable<Expense[]> {
    return this.api.post<Expense[]>(`/properties/${propertyId}/expenses`, data);
  }

  update(id: string, data: Partial<ExpenseCreate>): Observable<Expense> {
    return this.api.put<Expense>(`/expenses/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/expenses/${id}`);
  }

  generateRecurring(propertyId: string, year: number, month: number): Observable<Expense[]> {
    return this.api.post<Expense[]>(`/properties/${propertyId}/expenses/generate-recurring`, { year, month });
  }

  markDone(id: string): Observable<Expense> {
    return this.api.patch<Expense>(`/expenses/${id}/mark-done`, {});
  }

  unmarkDone(id: string): Observable<Expense> {
    return this.api.patch<Expense>(`/expenses/${id}/unmark-done`, {});
  }
}
