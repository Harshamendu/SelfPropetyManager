import { Component, Input, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialog } from '@angular/material/dialog';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { FormsModule } from '@angular/forms';
import { RentalPaymentService } from '../services/rental-payment.service';
import { RentalPayment } from '../models/rental-payment.model';
import { PaymentFormComponent } from '../payment-form/payment-form.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';
import { CategoryService } from '../../categories/services/category.service';
import { Category } from '../../categories/models/category.model';

@Component({
  selector: 'app-payment-list',
  standalone: true,
  imports: [
    CommonModule, MatTableModule, MatButtonModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, FormsModule, CurrencyFormatPipe,
    MatCheckboxModule, MatTooltipModule, MatChipsModule
  ],
  templateUrl: './payment-list.component.html',
  styleUrl: './payment-list.component.scss'
})
export class PaymentListComponent implements OnInit {
  @Input({ required: true }) propertyId!: string;

  private paymentService = inject(RentalPaymentService);
  private categoryService = inject(CategoryService);
  private dialog = inject(MatDialog);

  payments: RentalPayment[] = [];
  categories: Category[] = [];
  displayedColumns = ['status', 'payment_date', 'category', 'amount', 'period', 'payment_method', 'actions'];
  loading = true;
  selectedYear: number = new Date().getFullYear();
  years: number[] = [];
  totalPayments = 0;
  today = new Date().toISOString().split('T')[0];

  ngOnInit(): void {
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= currentYear - 5; y--) {
      this.years.push(y);
    }
    this.loadCategories();
    this.loadPayments();
  }

  loadCategories(): void {
    this.categoryService.getAll('payment', this.propertyId).subscribe({
      next: (cats) => this.categories = cats
    });
  }

  loadPayments(): void {
    this.loading = true;
    this.paymentService.getByProperty(this.propertyId, this.selectedYear).subscribe({
      next: (payments) => {
        this.payments = payments;
        this.totalPayments = payments.reduce((sum, p) => sum + p.amount, 0);
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  isFuture(payment: RentalPayment): boolean {
    return payment.payment_date > this.today;
  }

  isPastDue(payment: RentalPayment): boolean {
    return !payment.is_marked_done && payment.payment_date <= this.today;
  }

  requiresMarking(payment: RentalPayment): boolean {
    if (!payment.category) return true;
    const cat = this.categories.find(c => c.name === payment.category);
    return cat?.requires_marking ?? true;
  }

  toggleMarkDone(payment: RentalPayment): void {
    const request$ = payment.is_marked_done
      ? this.paymentService.unmarkDone(payment.id)
      : this.paymentService.markDone(payment.id);
    request$.subscribe({ next: () => this.loadPayments() });
  }

  addPayment(): void {
    const dialogRef = this.dialog.open(PaymentFormComponent, {
      width: '550px',
      data: { propertyId: this.propertyId }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        this.loadPayments();
      }
    });
  }

  editPayment(payment: RentalPayment): void {
    const dialogRef = this.dialog.open(PaymentFormComponent, {
      width: '550px',
      data: { propertyId: this.propertyId, payment }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        this.loadPayments();
      }
    });
  }

  deletePayment(payment: RentalPayment): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Payment',
        message: `Delete payment of $${payment.amount.toFixed(2)} on ${payment.payment_date}?`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.paymentService.delete(payment.id).subscribe({
          next: () => this.loadPayments()
        });
      }
    });
  }

  onYearChange(): void {
    this.loadPayments();
  }
}
