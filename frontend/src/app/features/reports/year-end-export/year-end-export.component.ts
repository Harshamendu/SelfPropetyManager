import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ReportService } from '../services/report.service';
import { PropertyService } from '@features/properties/services/property.service';
import { Property } from '@features/properties/models/property.model';

@Component({
  selector: 'app-year-end-export',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatFormFieldModule, MatSelectModule, MatButtonModule, MatIconModule],
  templateUrl: './year-end-export.component.html',
  styleUrl: './year-end-export.component.scss'
})
export class YearEndExportComponent implements OnInit {
  private reportService = inject(ReportService);
  private propertyService = inject(PropertyService);

  selectedYear: number = new Date().getFullYear();
  selectedPropertyId: string | null = null;
  years: number[] = [];
  properties: Property[] = [];
  downloading = false;

  ngOnInit(): void {
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= currentYear - 10; y--) {
      this.years.push(y);
    }

    this.propertyService.getAll().subscribe({
      next: (props) => this.properties = props
    });
  }

  download(): void {
    this.downloading = true;
    this.reportService.downloadYearEnd(this.selectedYear, this.selectedPropertyId || undefined).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const suffix = this.selectedPropertyId ? `_property_${this.selectedPropertyId}` : '';
        a.download = `year_end_report_${this.selectedYear}${suffix}.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
        this.downloading = false;
      },
      error: () => this.downloading = false
    });
  }
}
