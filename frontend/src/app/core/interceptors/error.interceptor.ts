import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An unexpected error occurred';

      if (error.error instanceof ErrorEvent) {
        errorMessage = `Client error: ${error.error.message}`;
      } else {
        errorMessage = `Server error: ${error.status} - ${error.error?.detail || error.statusText}`;
      }

      console.error('HTTP Error:', errorMessage, error);
      return throwError(() => error);
    })
  );
};
