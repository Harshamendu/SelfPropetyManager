import { Component, inject, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { PropertyService } from '@features/properties/services/property.service';
import { DocumentGenService } from '../services/document-gen.service';
import { Property } from '@features/properties/models/property.model';
import { DocumentTemplate, TemplateVariable } from '../models/template.model';

@Component({
  selector: 'app-generate-dialog',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatDialogModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatButtonModule, MatIconModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './generate-dialog.component.html',
  styleUrl: './generate-dialog.component.scss'
})
export class GenerateDialogComponent implements OnInit {
  private propertyService = inject(PropertyService);
  private docGenService = inject(DocumentGenService);
  private dialogRef = inject(MatDialogRef<GenerateDialogComponent>);

  template: DocumentTemplate;
  properties: Property[] = [];
  selectedPropertyId = '';
  variables: Record<string, string> = {};
  loading = false;
  contextLoaded = false;
  previewText = '';
  showPreview = false;

  constructor(@Inject(MAT_DIALOG_DATA) public data: { template: DocumentTemplate }) {
    this.template = data.template;
    // Initialize variables with defaults
    this.template.variables.forEach(v => {
      this.variables[v.name] = v.default_value || '';
    });
  }

  ngOnInit(): void {
    this.propertyService.getAll().subscribe({
      next: (props) => this.properties = props
    });
  }

  onPropertyChange(): void {
    if (!this.selectedPropertyId) return;

    this.loading = true;
    this.docGenService.getContext(this.selectedPropertyId).subscribe({
      next: (context) => {
        // Auto-fill variables from context where keys match
        for (const [key, value] of Object.entries(context)) {
          if (key in this.variables && value) {
            this.variables[key] = value;
          }
        }
        this.contextLoaded = true;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  preview(): void {
    this.loading = true;
    this.docGenService.preview(this.template.id, this.variables).subscribe({
      next: (result) => {
        this.previewText = result.rendered;
        this.showPreview = true;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  editFields(): void {
    this.showPreview = false;
  }

  generate(): void {
    this.loading = true;
    this.docGenService.generate(this.template.id, this.variables).subscribe({
      next: (blob) => {
        const pdfBlob = new Blob([blob], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(pdfBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.template.name}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.loading = false;
        this.dialogRef.close(true);
      },
      error: () => this.loading = false
    });
  }

  cancel(): void {
    this.dialogRef.close(false);
  }
}
