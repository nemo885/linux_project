
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.6.0"
    }
  }
}

provider "docker" {}

variable "db_password" {
  type      = string
  sensitive = true
}

resource "docker_network" "todo" {
  name = "todo-net"
}

resource "docker_volume" "postgres_data" {
  name = "tf-postgres-data"
}

resource "docker_image" "postgres" {
  name         = "postgres:16"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name         = "postgres"
  image        = docker_image.postgres.image_id
  wait         = true
  wait_timeout = 60

  env = [
    "POSTGRES_DB=tododb",
    "POSTGRES_USER=todouser",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  networks_advanced {
    name    = docker_network.todo.name
    aliases = ["postgres"]
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready  -U todouser -d tododb"]
    interval = "5s"
    timeout  = "5s"
    retries  = 5
  }


}
resource "docker_image" "backend" {
  name = "todo-backend:latest"
  build {
    context = "${path.module}/../backend"
  }
}

resource "docker_container" "backend" {
  name  = "todo-backend"
  image = docker_image.backend.image_id

  env = [
    "DB_HOST=postgres",
    "DB_PORT=5432",
    "DB_NAME=tododb",
    "DB_USER=todouser",
    "DB_PASSWORD=${var.db_password}",
  ]

  ports {
    internal = 8000
    external = 8001
  }

  networks_advanced {
    name = docker_network.todo.name
  }

  depends_on = [docker_container.postgres]
}
