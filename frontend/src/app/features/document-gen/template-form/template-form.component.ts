import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { DocumentGenService } from '../services/document-gen.service';

@Component({
  selector: 'app-template-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatButtonModule, MatIconModule, MatCardModule
  ],
  templateUrl: './template-form.component.html',
  styleUrl: './template-form.component.scss'
})
export class TemplateFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private docGenService = inject(DocumentGenService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  form!: FormGroup;
  isEditMode = false;
  templateId: string | null = null;
  loading = false;

  get variablesArray(): FormArray {
    return this.form.get('variables') as FormArray;
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      template_body: ['', Validators.required],
      variables: this.fb.array([])
    });

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.templateId = id;
      this.loadTemplate(this.templateId);
    }
  }

  loadTemplate(id: string): void {
    this.docGenService.getById(id).subscribe({
      next: (template) => {
        this.form.patchValue({
          name: template.name,
          description: template.description,
          template_body: template.template_body
        });

        template.variables.forEach(v => {
          this.variablesArray.push(this.fb.group({
            name: [v.name, Validators.required],
            label: [v.label, Validators.required],
            default_value: [v.default_value || '']
          }));
        });
      }
    });
  }

  addVariable(): void {
    this.variablesArray.push(this.fb.group({
      name: ['', Validators.required],
      label: ['', Validators.required],
      default_value: ['']
    }));
  }

  removeVariable(index: number): void {
    this.variablesArray.removeAt(index);
  }

  onSubmit(): void {
    if (this.form.invalid) return;

    this.loading = true;
    const request$ = this.isEditMode && this.templateId
      ? this.docGenService.update(this.templateId, this.form.value)
      : this.docGenService.create(this.form.value);

    request$.subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/document-templates']);
      },
      error: () => this.loading = false
    });
  }

  cancel(): void {
    this.router.navigate(['/document-templates']);
  }
}
