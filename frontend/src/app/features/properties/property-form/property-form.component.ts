import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { PropertyService } from '../services/property.service';

@Component({
  selector: 'app-property-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatDatepickerModule, MatNativeDateModule, MatButtonModule, MatCardModule
  ],
  templateUrl: './property-form.component.html',
  styleUrl: './property-form.component.scss'
})
export class PropertyFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private propertyService = inject(PropertyService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  form!: FormGroup;
  isEditMode = false;
  propertyId: string | null = null;
  loading = false;

  propertyTypes = [
    'Single Family Home',
    'Multi Family Home',
    'Condo',
    'Townhouse',
    'Apartment',
    'Commercial',
    'Land',
    'Other'
  ];

  ngOnInit(): void {
    this.form = this.fb.group({
      name: ['', Validators.required],
      address_line1: ['', Validators.required],
      address_line2: [''],
      city: ['', Validators.required],
      state: ['', Validators.required],
      zip_code: ['', Validators.required],
      property_type: ['', Validators.required],
      purchase_date: [null],
      purchase_price: [null],
      notes: [''],
      landlord_name: [''],
      landlord_phone: [''],
      landlord_email: [''],
      landlord_address: ['']
    });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.propertyId = id;
      this.loadProperty(this.propertyId);
    }
  }

  loadProperty(id: string): void {
    this.propertyService.getById(id).subscribe({
      next: (property) => {
        this.form.patchValue({
          ...property,
          purchase_date: property.purchase_date ? new Date(property.purchase_date) : null
        });
      }
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;

    this.loading = true;
    const formValue = { ...this.form.value };

    if (formValue.purchase_date) {
      const d = new Date(formValue.purchase_date);
      formValue.purchase_date = d.toISOString().split('T')[0];
    }

    const request$ = this.isEditMode && this.propertyId
      ? this.propertyService.update(this.propertyId, formValue)
      : this.propertyService.create(formValue);

    request$.subscribe({
      next: (property) => {
        this.loading = false;
        this.router.navigate(['/properties', property.id]);
      },
      error: () => this.loading = false
    });
  }

  cancel(): void {
    if (this.isEditMode && this.propertyId) {
      this.router.navigate(['/properties', this.propertyId]);
    } else {
      this.router.navigate(['/properties']);
    }
  }
}
