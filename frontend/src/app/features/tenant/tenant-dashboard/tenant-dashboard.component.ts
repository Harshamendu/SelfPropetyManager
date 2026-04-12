import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { PropertyService } from '@features/properties/services/property.service';
import { Property, PropertySummary } from '@features/properties/models/property.model';
import { RentalPaymentService } from '@features/rental-payments/services/rental-payment.service';
import { RentalPayment } from '@features/rental-payments/models/rental-payment.model';
import { ReminderService } from '@features/reminders/services/reminder.service';
import { Reminder } from '@features/reminders/models/reminder.model';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';
import { AuthService } from '@core/services/auth.service';

@Component({
  selector: 'app-tenant-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatTableModule,
    MatChipsModule,
    MatListModule,
    MatDividerModule,
    CurrencyFormatPipe,
  ],
  templateUrl: './tenant-dashboard.component.html',
  styleUrl: './tenant-dashboard.component.scss',
})
export class TenantDashboardComponent implements OnInit {
  private propertyService = inject(PropertyService);
  private rentalPaymentService = inject(RentalPaymentService);
  private reminderService = inject(ReminderService);
  private authService = inject(AuthService);

  loading = true;
  property?: Property;
  summary?: PropertySummary;
  payments: RentalPayment[] = [];
  upcomingReminders: Reminder[] = [];
  currentYear = new Date().getFullYear();

  paymentColumns = ['period', 'payment_date', 'amount', 'payment_method', 'status'];

  get tenantName(): string {
    return this.authService.currentUser?.full_name ?? 'Tenant';
  }

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.propertyService.getAll().subscribe({
      next: (properties) => {
        if (properties.length === 0) {
          this.loading = false;
          return;
        }
        // Tenant should see exactly one property (the one their contact is linked to).
        this.property = properties[0];
        this.loadPropertyDetails(this.property.id);
      },
      error: () => (this.loading = false),
    });
  }

  private loadPropertyDetails(propertyId: string): void {
    forkJoin({
      summary: this.propertyService
        .getSummary(propertyId, this.currentYear)
        .pipe(catchError(() => of(undefined))),
      payments: this.rentalPaymentService
        .getByProperty(propertyId, this.currentYear)
        .pipe(catchError(() => of([] as RentalPayment[]))),
      reminders: this.reminderService
        .getByProperty(propertyId)
        .pipe(catchError(() => of([] as Reminder[]))),
    }).subscribe({
      next: ({ summary, payments, reminders }) => {
        this.summary = summary;
        this.payments = [...payments].sort(
          (a, b) => new Date(b.payment_date).getTime() - new Date(a.payment_date).getTime(),
        );
        const now = Date.now();
        this.upcomingReminders = reminders
          .filter((r) => !r.is_completed && new Date(r.due_date).getTime() >= now)
          .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
          .slice(0, 5);
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  get totalPaidYtd(): number {
    return this.payments
      .filter((p) => p.is_marked_done)
      .reduce((sum, p) => sum + Number(p.amount || 0), 0);
  }

  get nextDuePayment(): RentalPayment | undefined {
    return this.payments.find((p) => !p.is_marked_done);
  }
}
