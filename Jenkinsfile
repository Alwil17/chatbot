pipeline {
    agent any

    options {
        ansiColor('xterm')
    }

    environment {
        // Define environment variables here
        BOT_NAME = 'awesome-bot'
        // BOT_TOKEN = credentials('telegram-bot-token')
    }

    stages {
        stage('Initialisation') {
            steps {
                sh "echo Branch name ${BRANCH_NAME}"
                sh "make venv && make install"
            }
        }


        stage('Tests Unitaires') {
            steps {
                script {
                    // Add your test commands here
                    echo "Running tests..."
                    sh "make test"
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    // Add your build commands here
                    echo "Building the project..."
                    sh "make build"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Add your deployment commands here
                    echo "Deploying the project..."
                    sh "make deploy env=${BRANCH_NAME}"
                }
            }
        }

        stage('Test endpoint'){
            steps {
                script {
                    // Add your endpoint testing commands here
                    echo "Testing the endpoint..."
                    sh "make test-endpoint"
                }
            }
        }
    }

    post {
        always {
            script {
                // Add your post-build actions here
                echo "Post-build actions..."
            }
        }
        success {
            script {
                // Notify success
                echo "Build succeeded!"
                // Uncomment the line below to send a message to Telegram
                // sh "curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage -d chat_id=<CHAT_ID> -d text='Build succeeded!'"
            }
        }
        failure {
            script {
                // Notify failure
                echo "Build failed!"
                // Uncomment the line below to send a message to Telegram
                // sh "curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage -d chat_id=<CHAT_ID> -d text='Build failed!'"
            }
        }
    }

}