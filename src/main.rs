use axum::{routing::get, Router};
use std::net::SocketAddr;
use tokio::net::TcpListener;

async fn hello_blindtest() -> &'static str {
    "Hello Blindtest!"
}

#[tokio::main]
async fn main() {
    let router = Router::new().route("/", get(hello_blindtest));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let tcp = TcpListener::bind(&addr).await.unwrap();
    println!("Serveur en cours d'exécution sur http://{}", addr);
    axum::serve(tcp, router).await.unwrap();
}
