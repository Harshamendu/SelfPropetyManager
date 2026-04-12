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
import { ExpenseService } from '../services/expense.service';
import { Expense } from '../models/expense.model';
import { CategoryService } from '../../categories/services/category.service';
import { Category } from '../../categories/models/category.model';

@Component({
  selector: 'app-expense-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, FormsModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatDatepickerModule, MatNativeDateModule,
    MatButtonModule, MatCheckboxModule, MatIconModule
  ],
  templateUrl: './expense-form.component.html'
})
export class ExpenseFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ExpenseFormComponent>);
  private data: { propertyId: string; expense?: Expense } = inject(MAT_DIALOG_DATA);
  private expenseService = inject(ExpenseService);
  private categoryService = inject(CategoryService);

  form!: FormGroup;
  categories: Category[] = [];
  isEditMode = false;
  saving = false;
  addingCategory = false;
  newCategoryName = '';

  frequencies = ['monthly', 'quarterly', 'annually'];

  ngOnInit(): void {
    this.isEditMode = !!this.data.expense;
    this.loadCategories();

    this.form = this.fb.group({
      category: [this.data.expense?.category || '', Validators.required],
      description: [this.data.expense?.description || '', Validators.required],
      amount: [this.data.expense?.amount || null, [Validators.required, Validators.min(0.01)]],
      date: [this.data.expense?.date ? new Date(this.data.expense.date) : new Date(), Validators.required],
      vendor: [this.data.expense?.vendor || ''],
      is_recurring: [this.data.expense?.is_recurring || false],
      recurrence_rule: [this.data.expense?.recurrence_rule || ''],
      recurring_day: [this.data.expense?.recurring_day || null]
    });
  }

  loadCategories(): void {
    this.categoryService.getAll('expense', this.data.propertyId).subscribe({
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
      category_type: 'expense',
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
    if (formValue.date) {
      const d = new Date(formValue.date);
      formValue.date = d.toISOString().split('T')[0];
    }

    const done = () => {
      this.saving = false;
      this.dialogRef.close(true);
    };
    const fail = () => this.saving = false;

    if (this.isEditMode) {
      this.expenseService.update(this.data.expense!.id, formValue).subscribe({ next: done, error: fail });
    } else {
      this.expenseService.create(this.data.propertyId, formValue).subscribe({ next: done, error: fail });
    }
  }

  cancel(): void {
    this.dialogRef.close(false);
  }
}
