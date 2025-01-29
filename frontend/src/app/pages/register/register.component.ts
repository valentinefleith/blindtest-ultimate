import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-register',
  standalone: true,
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
  imports: [FormsModule, CommonModule],
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  message = '';
  errorMessage = '';

  constructor(private userService: UserService) {}

register() {
    this.message = '';
    this.errorMessage = ''; // Réinitialise les messages

    this.userService.register(this.username, this.email, this.password).subscribe(
      response => {
        this.message = 'Inscription réussie ! Vous pouvez vous connecter.';
      },
      error => {
        if (error.status === 400) {
          if (error.error.detail === "Le nom d'utilisateur est déjà pris.") {
            this.errorMessage = "Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre.";
          } else if (error.error.detail === "L'adresse email est déjà utilisée.") {
            this.errorMessage = "Cet email est déjà enregistré. Essayez de vous connecter ou utilisez un autre email.";
          } else {
            this.errorMessage = error.error.detail;
          }
        } else {
          this.errorMessage = "Une erreur s'est produite. Veuillez réessayer.";
        }
      }
    );
  }
}
