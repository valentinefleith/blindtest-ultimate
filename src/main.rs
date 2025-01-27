use axum::Extension;
use dotenv::dotenv;
use std::env;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;

mod config;
mod db;
mod models;
mod routes;

#[tokio::main]
async fn main() {
    dotenv().ok();
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL not set");
    let pool = config::init_db(&db_url).await;
    let shared_pool = Arc::new(pool);
    let app = routes::create_router().layer(Extension(shared_pool));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    let tcp = TcpListener::bind(&addr).await.unwrap();
    println!("Serveur en cours d'exécution sur http://{}", addr);
    axum::serve(tcp, app).await.unwrap();
}
