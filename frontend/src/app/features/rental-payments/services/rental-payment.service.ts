import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';
import { RentalPayment, RentalPaymentCreate } from '../models/rental-payment.model';

@Injectable({ providedIn: 'root' })
export class RentalPaymentService {
  private api = inject(ApiService);

  getByProperty(propertyId: string, year?: number): Observable<RentalPayment[]> {
    const params: Record<string, number> = {};
    if (year) params['year'] = year;
    return this.api.get<RentalPayment[]>(`/properties/${propertyId}/rental-payments`, params);
  }

  create(propertyId: string, data: RentalPaymentCreate): Observable<RentalPayment[]> {
    return this.api.post<RentalPayment[]>(`/properties/${propertyId}/rental-payments`, data);
  }

  update(id: string, data: Partial<RentalPaymentCreate>): Observable<RentalPayment> {
    return this.api.put<RentalPayment>(`/rental-payments/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete<void>(`/rental-payments/${id}`);
  }

  markDone(id: string): Observable<RentalPayment> {
    return this.api.patch<RentalPayment>(`/rental-payments/${id}/mark-done`, {});
  }

  unmarkDone(id: string): Observable<RentalPayment> {
    return this.api.patch<RentalPayment>(`/rental-payments/${id}/unmark-done`, {});
  }
}
