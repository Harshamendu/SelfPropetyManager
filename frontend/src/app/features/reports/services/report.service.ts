import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '@core/services/api.service';

@Injectable({ providedIn: 'root' })
export class ReportService {
  private api = inject(ApiService);

  downloadYearEnd(year: number, propertyId?: string): Observable<Blob> {
    const path = propertyId
      ? `/reports/year-end/${year}/${propertyId}`
      : `/reports/year-end/${year}`;
    return this.api.downloadBlob(path);
  }

  getSummary(year: number): Observable<unknown> {
    return this.api.get(`/reports/summary/${year}`);
  }
}
