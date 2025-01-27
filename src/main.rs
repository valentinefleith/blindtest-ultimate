use axum::Extension;
use sqlx::SqlitePool;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;

mod routes;

#[tokio::main]
async fn main() {
    let pool = SqlitePool::connect("sqlite://blindtest.db").await.unwrap();
    let shared_pool = Arc::new(pool);
    let app = routes::create_router().layer(Extension(shared_pool));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let tcp = TcpListener::bind(&addr).await.unwrap();
    println!("Serveur en cours d'exécution sur http://{}", addr);
    axum::serve(tcp, app).await.unwrap();
}
