import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:8000/api'; // URL du backend FastAPI

  constructor(private http: HttpClient) {}

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/register`, { username, email, password });
  }

login(username: string, password: string): Observable<any> {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);

  return this.http.post(`${this.apiUrl}/login`, body.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
}
}
