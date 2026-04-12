import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { forkJoin } from 'rxjs';
import { PropertyService } from '@features/properties/services/property.service';
import { Property, PropertySummary } from '@features/properties/models/property.model';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CurrencyFormatPipe } from '@shared/pipes/currency-format.pipe';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatTooltipModule, CurrencyFormatPipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  private propertyService = inject(PropertyService);
  private router = inject(Router);

  properties: Property[] = [];
  summaries: Map<string, PropertySummary> = new Map();
  loading = true;
  currentYear = new Date().getFullYear();
  showSensitive = false;

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.propertyService.getAll().subscribe({
      next: (properties) => {
        this.properties = properties;

        if (properties.length === 0) {
          this.loading = false;
          return;
        }

        const summaryRequests = properties.map(p =>
          this.propertyService.getSummary(p.id, this.currentYear)
        );

        forkJoin(summaryRequests).subscribe({
          next: (summaries) => {
            summaries.forEach(s => this.summaries.set(s.id, s));
            this.loading = false;
          },
          error: () => this.loading = false
        });
      },
      error: () => this.loading = false
    });
  }

  getSummary(propertyId: string): PropertySummary | undefined {
    return this.summaries.get(propertyId);
  }

  viewProperty(id: string): void {
    this.router.navigate(['/properties', id]);
  }

  addProperty(): void {
    this.router.navigate(['/properties/new']);
  }

  toggleSensitive(): void {
    this.showSensitive = !this.showSensitive;
  }
}
