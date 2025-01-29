import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { RegisterComponent } from './pages/register/register.component';
import { LoginComponent } from './pages/login/login.component';

export const routes: Routes = [
  { path: '', component: HomeComponent }, // Accueil
  { path: 'register', component: RegisterComponent }, // Inscription
  { path: 'login', component: LoginComponent }, // Connexion
];
