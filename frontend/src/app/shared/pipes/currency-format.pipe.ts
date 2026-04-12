import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'currencyFormat',
  standalone: true
})
export class CurrencyFormatPipe implements PipeTransform {
  transform(value: number | null | undefined, symbol = '$'): string {
    if (value === null || value === undefined || isNaN(value)) {
      return `${symbol}0.00`;
    }
    const formatted = Math.abs(value).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    return value < 0 ? `-${symbol}${formatted}` : `${symbol}${formatted}`;
  }
}
