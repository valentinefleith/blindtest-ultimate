use blindtest::routes::create_router;
use reqwest::Client;
use std::net::SocketAddr;
use tokio::net::TcpListener;

async fn spawn_server() -> String {
    let router = create_router();
    let addr = SocketAddr::from(([127, 0, 0, 1], 0)); // Port aléatoire
    let listener = TcpListener::bind(addr).await.unwrap();
    let port = listener.local_addr().unwrap().port();
    tokio::spawn(async move {
        axum::serve(listener, router).await.unwrap();
    });

    format!("http://127.0.0.1:{}", port)
}

#[tokio::test]
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
