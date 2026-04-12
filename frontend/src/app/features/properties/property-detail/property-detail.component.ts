import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { Subscription } from 'rxjs';
import { PropertyService } from '../services/property.service';
import { Property } from '../models/property.model';
import { DocumentListComponent } from '@features/documents/document-list/document-list.component';
import { ExpenseListComponent } from '@features/expenses/expense-list/expense-list.component';
import { PaymentListComponent } from '@features/rental-payments/payment-list/payment-list.component';
import { ContactListComponent } from '@features/contacts/contact-list/contact-list.component';
import { ReminderListComponent } from '@features/reminders/reminder-list/reminder-list.component';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';

@Component({
  selector: 'app-property-detail',
  standalone: true,
  imports: [
    CommonModule, MatTabsModule, MatButtonModule, MatIconModule, MatCardModule,
    DocumentListComponent, ExpenseListComponent, PaymentListComponent,
    ContactListComponent, ReminderListComponent, CurrencyFormatPipe
  ],
  templateUrl: './property-detail.component.html',
  styleUrl: './property-detail.component.scss'
})
export class PropertyDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private propertyService = inject(PropertyService);
  private routeSub!: Subscription;

  property: Property | null = null;
  loading = true;

  ngOnInit(): void {
    this.routeSub = this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.loadProperty(id);
      }
    });
  }

  ngOnDestroy(): void {
    this.routeSub?.unsubscribe();
  }

  loadProperty(id: string): void {
    this.property = null;
    this.loading = true;
    this.propertyService.getById(id).subscribe({
      next: (property) => {
        this.property = property;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.router.navigate(['/properties']);
      }
    });
  }

  editProperty(): void {
    if (this.property) {
      this.router.navigate(['/properties', this.property.id, 'edit']);
    }
  }

  goBack(): void {
    this.router.navigate(['/properties']);
  }
}
