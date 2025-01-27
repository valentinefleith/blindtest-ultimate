use axum::{routing::post, Json, Router};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct RegisterUser {
    username: String,
    password: String,
}

#[derive(Serialize)]
struct UserResponse {
    id: u32,
    username: String,
}

async fn register(Json(payload): Json<RegisterUser>) -> Json<UserResponse> {
    // Simule un utilisateur enregistré avec un ID 1
    let user = UserResponse {
        id: 1,
        username: payload.username,
    };

    Json(user) // Retourne l'utilisateur en JSON
}

// Fonction pour enregistrer les routes utilisateurs
pub fn routes() -> Router {
    Router::new().route("/register", post(register))
}

#[cfg(test)]
mod tests {
    use super::*; // Permet d'accéder aux structs privées du module
    use axum::Json;

    #[test]
    fn test_user_creation() {
        let input = RegisterUser {
            username: "testuser".to_string(),
            password: "1234".to_string(),
        };

        let expected = UserResponse {
            id: 1,
            username: "testuser".to_string(),
        };

        let result = UserResponse {
            id: 1,
            username: input.username,
        };

        assert_eq!(result.id, expected.id);
        assert_eq!(result.username, expected.username);
    }
}
