#![allow(dead_code, unused_imports, unused_variables)]

use axum::extract::Extension;
use blindtest::routes::create_router;
use reqwest::Client;
use sqlx::sqlite::SqlitePoolOptions;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;

async fn spawn_server() -> String {
    let pool = SqlitePoolOptions::new()
        .connect("sqlite::memory:")
        .await
        .expect("Failed to connect to database");

    // Exécute la migration pour créer la table `users`
    sqlx::migrate!().run(&pool).await.expect("Migration failed");

    let app = create_router().layer(Extension(Arc::new(pool)));
    let addr = SocketAddr::from(([127, 0, 0, 1], 0)); // Port aléatoire
    let listener = TcpListener::bind(addr).await.unwrap();
    let port = listener.local_addr().unwrap().port();
    tokio::spawn(async move {
        axum::serve(listener, app).await.unwrap();
    });

    format!("http://127.0.0.1:{}", port)
}

//#[tokio::test]
async fn test_register_user() {
    let base_url = spawn_server().await;
    let client = Client::new();

    let response = client
        .post(format!("{}/api/users/register", base_url))
        .json(&serde_json::json!({
            "username": "testuser",
            "password": "1234"
        }))
        .send()
        .await
        .unwrap();

    assert_eq!(response.status(), 200);

    let body: serde_json::Value = response.json().await.unwrap();
    assert_eq!(body["username"], "testuser");
}
