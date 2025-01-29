import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenKey = 'token';
  private isLoggedInSubject = new BehaviorSubject<boolean>(this.checkToken());

  constructor() {}

  private checkToken(): boolean {
    return typeof window !== 'undefined' && !!localStorage.getItem(this.tokenKey);
  }

  isLoggedIn$ = this.isLoggedInSubject.asObservable(); // 👈 Observable pour la navbar

  login(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.tokenKey, token);
      this.isLoggedInSubject.next(true); // 🔄 Met à jour la navbar après connexion
    }
  }

  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
      this.isLoggedInSubject.next(false); // 🔄 Met à jour la navbar après déconnexion
    }
  }

  //isLoggedIn(): boolean {
    //return !!localStorage.getItem(this.tokenKey);
  //}

  isLoggedIn(): boolean {
    return this.isLoggedInSubject.getValue(); // ✅ Permet d'obtenir l'état actuel
  }

  getToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem(this.tokenKey);
  }

  getUserInfo(): any {
    const token = this.getToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1])); // Décode le payload JWT
      return payload; // Retourne les infos utilisateur (ex: username)
    } catch (error) {
      return null;
    }
  }
}
