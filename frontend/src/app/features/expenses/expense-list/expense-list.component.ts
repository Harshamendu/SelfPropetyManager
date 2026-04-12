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
import { FormsModule } from '@angular/forms';
import { ExpenseService } from '../services/expense.service';
import { Expense } from '../models/expense.model';
import { ExpenseFormComponent } from '../expense-form/expense-form.component';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';
import { CategoryService } from '../../categories/services/category.service';
import { Category } from '../../categories/models/category.model';

@Component({
  selector: 'app-expense-list',
  standalone: true,
  imports: [
    CommonModule, MatTableModule, MatButtonModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, FormsModule, CurrencyFormatPipe,
    MatCheckboxModule, MatTooltipModule
  ],
  templateUrl: './expense-list.component.html',
  styleUrl: './expense-list.component.scss'
})
export class ExpenseListComponent implements OnInit {
  @Input({ required: true }) propertyId!: string;

  private expenseService = inject(ExpenseService);
  private categoryService = inject(CategoryService);
  private dialog = inject(MatDialog);

  expenses: Expense[] = [];
  filteredExpenses: Expense[] = [];
  categories: Category[] = [];
  displayedColumns = ['status', 'date', 'category', 'description', 'vendor', 'amount', 'actions'];
  loading = true;
  selectedYear: number = new Date().getFullYear();
  selectedCategory = '';
  sortDirection: 'asc' | 'desc' = 'asc';
  sortField: 'date' | 'category' | 'amount' = 'date';
  years: number[] = [];
  totalExpenses = 0;
  today = new Date().toISOString().split('T')[0];

  ngOnInit(): void {
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= currentYear - 5; y--) {
      this.years.push(y);
    }
    this.loadCategories();
    this.loadExpenses();
  }

  loadCategories(): void {
    this.categoryService.getAll('expense', this.propertyId).subscribe({
      next: (cats) => this.categories = cats
    });
  }

  loadExpenses(): void {
    this.loading = true;
    const category = this.selectedCategory || undefined;
    this.expenseService.getByProperty(this.propertyId, this.selectedYear, category).subscribe({
      next: (expenses) => {
        this.expenses = expenses;
        this.applySort();
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  applySort(): void {
    const dir = this.sortDirection === 'asc' ? 1 : -1;
    this.filteredExpenses = [...this.expenses].sort((a, b) => {
      if (this.sortField === 'date') {
        return a.date.localeCompare(b.date) * dir;
      } else if (this.sortField === 'category') {
        return a.category.localeCompare(b.category) * dir;
      } else {
        return (a.amount - b.amount) * dir;
      }
    });
    this.totalExpenses = this.filteredExpenses.reduce((sum, e) => sum + Number(e.amount), 0);
  }

  onCategoryChange(): void {
    this.loadExpenses();
  }

  onSortChange(): void {
    this.applySort();
  }

  toggleSortDirection(): void {
    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    this.applySort();
  }

  isFuture(expense: Expense): boolean {
    return expense.date > this.today;
  }

  isPastDue(expense: Expense): boolean {
    return !expense.is_marked_done && expense.date <= this.today && this.requiresMarking(expense);
  }

  requiresMarking(expense: Expense): boolean {
    const cat = this.categories.find(c => c.name === expense.category);
    return cat?.requires_marking ?? false;
  }

  toggleMarkDone(expense: Expense): void {
    const request$ = expense.is_marked_done
      ? this.expenseService.unmarkDone(expense.id)
      : this.expenseService.markDone(expense.id);
    request$.subscribe({ next: () => this.loadExpenses() });
  }

  addExpense(): void {
    const dialogRef = this.dialog.open(ExpenseFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        this.loadExpenses();
      }
    });
  }

  editExpense(expense: Expense): void {
    const dialogRef = this.dialog.open(ExpenseFormComponent, {
      width: '500px',
      data: { propertyId: this.propertyId, expense }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCategories();
        this.loadExpenses();
      }
    });
  }

  deleteExpense(expense: Expense): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Expense',
        message: `Delete expense "${expense.description}" for $${expense.amount.toFixed(2)}?`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.expenseService.delete(expense.id).subscribe({
          next: () => this.loadExpenses()
        });
      }
    });
  }

  onYearChange(): void {
    this.loadExpenses();
  }
}
