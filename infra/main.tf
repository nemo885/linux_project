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
  name  = "postgres"
  image = docker_image.postgres.image_id

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
}
