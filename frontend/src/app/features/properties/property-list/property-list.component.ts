import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { PropertyService } from '../services/property.service';
import { Property } from '../models/property.model';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-property-list',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './property-list.component.html',
  styleUrl: './property-list.component.scss'
})
export class PropertyListComponent implements OnInit {
  private propertyService = inject(PropertyService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  properties: Property[] = [];
  loading = true;

  ngOnInit(): void {
    this.loadProperties();
  }

  loadProperties(): void {
    this.loading = true;
    this.propertyService.getAll().subscribe({
      next: (props) => {
        this.properties = props;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  addProperty(): void {
    this.router.navigate(['/properties/new']);
  }

  viewProperty(id: string): void {
    this.router.navigate(['/properties', id]);
  }

  editProperty(id: string, event: Event): void {
    event.stopPropagation();
    this.router.navigate(['/properties', id, 'edit']);
  }

  deleteProperty(property: Property, event: Event): void {
    event.stopPropagation();
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Property',
        message: `Are you sure you want to delete "${property.name}"? This will also delete all associated documents, expenses, payments, contacts, and reminders.`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.propertyService.delete(property.id).subscribe({
          next: () => this.loadProperties()
        });
      }
    });
  }
}
