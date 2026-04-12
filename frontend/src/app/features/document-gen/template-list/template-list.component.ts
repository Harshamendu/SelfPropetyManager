import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDialog } from '@angular/material/dialog';
import { DocumentGenService } from '../services/document-gen.service';
import { DocumentTemplate, US_STATES } from '../models/template.model';
import { ConfirmDialogComponent } from '@shared/components/confirm-dialog/confirm-dialog.component';
import { GenerateDialogComponent } from '../generate-dialog/generate-dialog.component';

@Component({
  selector: 'app-template-list',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule, MatFormFieldModule, MatSelectModule],
  templateUrl: './template-list.component.html',
  styleUrl: './template-list.component.scss'
})
export class TemplateListComponent implements OnInit {
  private docGenService = inject(DocumentGenService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  templates: DocumentTemplate[] = [];
  loading = true;
  states = US_STATES;
  selectedState = 'GA';

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.loading = true;
    this.docGenService.getAll(this.selectedState || undefined).subscribe({
      next: (templates) => {
        this.templates = templates;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  onStateChange(): void {
    this.loadTemplates();
  }

  createTemplate(): void {
    this.router.navigate(['/document-templates/new']);
  }

  editTemplate(id: string): void {
    this.router.navigate(['/document-templates', id, 'edit']);
  }

  deleteTemplate(template: DocumentTemplate): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Template',
        message: `Delete template "${template.name}"?`,
        confirmText: 'Delete'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.docGenService.delete(template.id).subscribe({
          next: () => this.loadTemplates()
        });
      }
    });
  }

  seedTemplates(): void {
    if (!this.selectedState) return;
    this.loading = true;
    this.docGenService.seedTemplates(this.selectedState).subscribe({
      next: () => this.loadTemplates(),
      error: () => this.loading = false
    });
  }

  generateDocument(template: DocumentTemplate): void {
    this.dialog.open(GenerateDialogComponent, {
      width: '800px',
      maxHeight: '90vh',
      data: { template }
    });
  }
}
