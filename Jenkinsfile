pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Start backend and postgres') {
            steps {
                sh 'docker compose up -d --build backend postgres'
            }
        }

        stage('Wait for postgres healthcheck') {
            steps {
                sh '''
                    POSTGRES_CONTAINER=$(docker compose ps -q postgres)
                    until [ "$(docker inspect -f '{{.State.Health.Status}}' $POSTGRES_CONTAINER)" = "healthy" ]; do
                        echo "Waiting for postgres..."
                        sleep 2
                    done
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh 'docker compose exec -T backend pytest'
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v'
        }
        failure {
            sh 'docker compose logs backend postgres'
        }
    }
}
