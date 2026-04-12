import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { RentalPaymentService } from '../services/rental-payment.service';
import { RentalPayment, PAYMENT_METHODS } from '../models/rental-payment.model';
import { CategoryService } from '../../categories/services/category.service';
import { Category } from '../../categories/models/category.model';

@Component({
  selector: 'app-payment-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, FormsModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatDatepickerModule, MatNativeDateModule,
    MatButtonModule, MatCheckboxModule, MatIconModule
  ],
  templateUrl: './payment-form.component.html'
})
export class PaymentFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<PaymentFormComponent>);
  private data: { propertyId: string; payment?: RentalPayment } = inject(MAT_DIALOG_DATA);
  private paymentService = inject(RentalPaymentService);
  private categoryService = inject(CategoryService);

  form!: FormGroup;
  paymentMethods = PAYMENT_METHODS;
  categories: Category[] = [];
  isEditMode = false;
  saving = false;
  addingCategory = false;
  newCategoryName = '';

  frequencies = ['monthly', 'quarterly', 'annually'];

  ngOnInit(): void {
    this.isEditMode = !!this.data.payment;
    this.loadCategories();
    const p = this.data.payment;

    this.form = this.fb.group({
      amount: [p?.amount || null, [Validators.required, Validators.min(0.01)]],
      payment_date: [p?.payment_date ? new Date(p.payment_date) : new Date(), Validators.required],
      payment_method: [p?.payment_method || '', Validators.required],
      period_start: [p?.period_start ? new Date(p.period_start) : new Date(), Validators.required],
      period_end: [p?.period_end ? new Date(p.period_end) : new Date(), Validators.required],
      category: [p?.category || ''],
      is_recurring: [p?.is_recurring || false],
      recurrence_rule: [p?.recurrence_rule || ''],
      recurring_day: [p?.recurring_day || 1],
      notes: [p?.notes || '']
    });
  }

  loadCategories(): void {
    this.categoryService.getAll('payment', this.data.propertyId).subscribe({
      next: (cats) => this.categories = cats
    });
  }

  onCategoryChange(categoryName: string): void {
    const cat = this.categories.find(c => c.name === categoryName);
    if (cat) {
      this.form.patchValue({
        is_recurring: cat.is_recurring,
        recurrence_rule: cat.default_recurrence_rule || ''
      });
    }
  }

  addCategory(name: string, isRecurring: boolean, requiresMarking: boolean): void {
    if (!name.trim()) return;
    this.categoryService.create({
      property_id: this.data.propertyId,
      name: name.trim(),
      category_type: 'payment',
      is_recurring: isRecurring,
      requires_marking: requiresMarking
    }).subscribe({
      next: (cat) => {
        this.categories.push(cat);
        this.form.patchValue({ category: cat.name });
        this.onCategoryChange(cat.name);
        this.addingCategory = false;
        this.newCategoryName = '';
      }
    });
  }

  save(): void {
    if (this.form.invalid) return;

    this.saving = true;
    const formValue = { ...this.form.value };

    ['payment_date', 'period_start', 'period_end'].forEach(field => {
      if (formValue[field]) {
        const d = new Date(formValue[field]);
        formValue[field] = d.toISOString().split('T')[0];
      }
    });

    const done = () => {
      this.saving = false;
      this.dialogRef.close(true);
    };
    const fail = () => this.saving = false;

    if (this.isEditMode) {
      this.paymentService.update(this.data.payment!.id, formValue).subscribe({ next: done, error: fail });
    } else {
      this.paymentService.create(this.data.propertyId, formValue).subscribe({ next: done, error: fail });
    }
  }

  cancel(): void {
    this.dialogRef.close(false);
  }
}
