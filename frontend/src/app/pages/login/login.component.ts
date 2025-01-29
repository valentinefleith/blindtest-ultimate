import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  imports: [FormsModule], // 👈 Ajout de FormsModule
})
export class LoginComponent {
  username = '';
  password = '';
  message = '';

  constructor(
    private userService: UserService,
    private authService: AuthService,
    private router: Router
  ) {}

  login() {
    this.userService.login(this.username, this.password).subscribe(
      response => {
        this.authService.login(response.access_token); // Stocke le token
        this.message = 'Connexion réussie !';
        this.router.navigate(['/profile']); // Redirige vers le profil
      },
      error => {
        this.message = 'Nom d’utilisateur ou mot de passe incorrect.';
        console.error(error);
      }
    );
  }
}
